import uuid
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger

from backend.models.trade import Account, Position, Order
from backend.schemas.trade import AccountCreate, OrderCreate

class TradeService:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Account Services ====================
    async def get_accounts(self, user_id: uuid.UUID) -> List[Account]:
        stmt = select(Account).where(Account.user_id == user_id)
        return self.db.execute(stmt).scalars().all()
        
    async def get_account_by_id(self, account_id: uuid.UUID) -> Optional[Account]:
        stmt = select(Account).where(Account.id == account_id)
        return self.db.execute(stmt).scalar_one_or_none()
        
    async def create_account(self, data: AccountCreate, user_id: uuid.UUID) -> Account:
        new_account = Account(
            name=data.name,
            account_type=data.account_type,
            broker=data.broker,
            account_number=data.account_number,
            initial_capital=data.initial_capital,
            current_capital=data.current_capital,
            status=data.status,
            user_id=user_id
        )
        self.db.add(new_account)
        self.db.commit()
        self.db.refresh(new_account)
        return new_account

    async def get_or_create_default_simulation_account(self, user_id: uuid.UUID) -> Account:
        """为用户兜底建立一个百万级基础模拟账户"""
        stmt = select(Account).where(Account.user_id == user_id, Account.account_type == "simulation")
        account = self.db.execute(stmt).scalar_one_or_none()
        if not account:
            account = await self.create_account(AccountCreate(
                name="Default Sandbox",
                account_type="simulation",
                initial_capital=1000000.0,
                current_capital=1000000.0,
            ), user_id)
        return account

    # ==================== Position Services ====================
    async def get_positions(self, account_id: uuid.UUID) -> List[Position]:
        stmt = select(Position).where(Position.account_id == account_id)
        return self.db.execute(stmt).scalars().all()

    # ==================== Order & Execution Services ====================
    async def get_orders(self, account_id: uuid.UUID, limit: int = 50) -> List[Order]:
        stmt = select(Order).where(Order.account_id == account_id).order_by(Order.created_at.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()

    async def place_order(self, data: OrderCreate) -> Order:
        """创建订单，并在 Paper Trading 模式下立刻执行虚拟撮合"""
        account = await self.get_account_by_id(data.account_id)
        if not account:
            raise ValueError("Invalid account ID")
            
        if account.status != "active":
             raise ValueError("Account is not active")

        # 1. 创建订单流
        new_order = Order(
            account_id=data.account_id,
            order_id=f"ORD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:6]}",
            symbol=data.symbol,
            side=data.side,
            order_type=data.order_type,
            quantity=data.quantity,
            price=data.price,
            status="pending"
        )
        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        # 2. 如果是模拟盘，立刻尝试执行它
        if account.account_type == "simulation":
             await self._execute_paper_trade(new_order.id)
             
        self.db.refresh(new_order)
        return new_order

    async def _execute_paper_trade(self, order_id: uuid.UUID):
        """Paper Trading 内部同步撮合器"""
        order = self.db.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
        if not order or order.status != "pending":
            return
            
        account = order.account
        
        # 获取基础执行价格（市价单随便兜底个假价格，限价取挂单价）
        # 在全真回测环境中这里要从上层的 data/market 拿最新 close，目前为演示使用 10.0
        exec_price = float(order.price) if order.price else 10.0
        cost = exec_price * order.quantity
        
        position = self.db.execute(
            select(Position).where(Position.account_id == account.id, Position.symbol == order.symbol)
        ).scalar_one_or_none()

        try:
            if order.side == "buy":
                # Check sufficient funds
                if account.current_capital < cost:
                    order.status = "failed"
                    self.db.commit()
                    return
                # Deduct funds
                account.current_capital -= cost
                
                # Add or update position
                if position:
                    total_qty = position.quantity + order.quantity
                    new_avg = ((float(position.avg_price or 0)) * position.quantity + cost) / total_qty
                    position.quantity = total_qty
                    position.avg_price = new_avg
                else:
                    position = Position(
                        account_id=account.id,
                        symbol=order.symbol,
                        quantity=order.quantity,
                        avg_price=exec_price,
                        market_price=exec_price
                    )
                    self.db.add(position)
                    
            elif order.side == "sell":
                 # Check sufficient positions
                 if not position or position.quantity < order.quantity:
                      order.status = "failed"
                      self.db.commit()
                      return
                      
                 # Add funds back
                 account.current_capital += cost
                 position.quantity -= order.quantity
                 
                 # clean zero pos
                 if position.quantity == 0:
                     self.db.delete(position)
            
            # Record execution metadata
            order.status = "filled"
            order.filled_quantity = order.quantity
            order.avg_fill_price = exec_price
            
            self.db.commit()
            logger.info(f"Paper Trade Executed: {order.side} {order.quantity} of {order.symbol} at {exec_price}")
            
        except Exception as e:
            self.db.rollback()
            order.status = "error"
            self.db.commit()
            logger.error(f"Paper execution failed: {str(e)}")

    # ==================== Fund Services (资金划拨) ====================
    async def fund_account(
        self, account_id: uuid.UUID, action: str, amount: float
    ) -> dict:
        """
        资金划拨：入金(deposit)增加可用资金，出金(withdraw)减少可用资金
        仅适用于模拟盘，实盘需对接真实券商通道
        """
        account = await self.get_account_by_id(account_id)
        if not account:
            raise ValueError("账户不存在")

        if account.status != "active":
            raise ValueError("账户状态异常，无法进行资金操作")

        balance_before = float(account.current_capital)

        if action == "deposit":
            account.current_capital = float(account.current_capital) + amount
            logger.info(f"Account {account_id} deposit: +{amount}, balance: {balance_before} -> {account.current_capital}")
        elif action == "withdraw":
            if float(account.current_capital) < amount:
                raise ValueError(f"余额不足，当前可用余额: {balance_before}")
            account.current_capital = float(account.current_capital) - amount
            logger.info(f"Account {account_id} withdraw: -{amount}, balance: {balance_before} -> {account.current_capital}")
        else:
            raise ValueError(f"不支持的操作类型: {action}")

        self.db.commit()
        self.db.refresh(account)

        return {
            "message": "充值成功" if action == "deposit" else "提现成功",
            "action": action,
            "amount": amount,
            "balance_before": balance_before,
            "balance_after": float(account.current_capital),
        }
