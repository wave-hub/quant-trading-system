import pandas as pd
import numpy as np
from datetime import timedelta
from loguru import logger
import uuid
from sqlalchemy.orm import Session

from backend.models.backtest import BacktestTask, BacktestTrade
from backend.models.market import MarketData, Stock

class FastSimulator:
    """MVP: 轻量级回测仿真沙盒引擎"""
    
    def __init__(self, task_id: uuid.UUID, db_session: Session):
        self.task_id = task_id
        self.db = db_session
        self.task = self.db.query(BacktestTask).filter(BacktestTask.id == task_id).first()
        
        self.capital = float(self.task.initial_capital)
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def _fetch_data(self):
        # 为了演示快速模拟，我们这里随机拉起一只常见标的在目标范围内的数据
        # 实际生产中应根据策略里的 universe 来取
        symbol = "000001.SZ"
        
        stmt = self.db.query(MarketData).join(Stock).filter(
            Stock.symbol == symbol,
            MarketData.trade_date >= self.task.start_date,
            MarketData.trade_date <= self.task.end_date
        ).order_by(MarketData.trade_date.asc())
        
        records = stmt.all()
        
        # Calculate MAs using pandas for the sandbox environment
        if records:
            df = pd.DataFrame([{
                "trade_date": r.trade_date,
                "close": float(r.close),
                "open": float(r.open),
                "high": float(r.high),
                "low": float(r.low),
                "volume": float(r.volume),
                "price": float(r.close)
            } for r in records])
            df.set_index("trade_date", inplace=True)
            df.sort_index(inplace=True)
            df["ma5"] = df["close"].rolling(window=5, min_periods=1).mean()
            df["ma20"] = df["close"].rolling(window=20, min_periods=1).mean()
            df.reset_index(inplace=True)
            
            # Reattach computed MAs back to records using a dictionary lookup
            lookup = {row["trade_date"]: row for idx, row in df.iterrows()}
            for r in records:
                row_data = lookup.get(r.trade_date)
                if row_data:
                    setattr(r, "ma5", row_data["ma5"])
                    setattr(r, "ma20", row_data["ma20"])
                    
        return symbol, records

    def run(self):
        try:
            self.task.status = "running"
            self.db.commit()
            
            logger.info(f"Starting engine simulation for task {self.task_id}")
            symbol, records = self._fetch_data()
            
            if not records:
                self.task.status = "failed"
                self.task.error_message = "No market data found in given date range."
                self.db.commit()
                return

            # Dummy execution loop
            total_days = len(records)
            for i, record in enumerate(records):
                current_date = record.trade_date.strftime("%Y-%m-%d")
                price = float(record.close)
                
                # Get dynamically computed MA values attached in _fetch_data
                ma5 = getattr(record, "ma5", None)
                ma20 = getattr(record, "ma20", None)
                
                # Fetch associated Strategy to execute custom code or fallback to standard crossover
                # MVP dual MA crossover strategy implementation
                # Trigger Buy if MA5 crosses above MA20. Target holding 100 shares.
                # Trigger Sell if MA5 crosses below MA20.
                
                if ma5 is not None and ma20 is not None:
                    if ma5 > ma20 and symbol not in self.positions:
                        # Buy 100 shares
                        cost = price * 100
                        if self.capital >= cost:
                            self.capital -= cost
                            self.positions[symbol] = 100
                            self.trades.append({
                                "backtest_id": self.task_id,
                                "symbol": symbol,
                                "side": "buy",
                                "quantity": 100,
                                "price": price,
                                "trade_date": record.trade_date
                            })
                    elif ma5 < ma20 and symbol in self.positions:
                        # Sell all
                        self.capital += price * self.positions[symbol]
                        self.trades.append({
                            "backtest_id": self.task_id,
                            "symbol": symbol,
                            "side": "sell",
                            "quantity": self.positions[symbol],
                            "price": price,
                            "trade_date": record.trade_date
                        })
                        del self.positions[symbol]
                
                # Calculate daily equity
                daily_equity = self.capital
                if symbol in self.positions:
                     daily_equity += price * self.positions[symbol]
                     
                self.equity_curve.append({
                    "date": current_date,
                    "equity": daily_equity
                })
                
                # Update progress
                if i % max(1, total_days // 10) == 0:
                    self.task.progress = int((i / total_days) * 100)
                    self.db.commit()
            
            # Record Trades
            new_trades = [BacktestTrade(**t) for t in self.trades]
            self.db.bulk_save_objects(new_trades)
            
            # Calculate metrics
            initial = float(self.task.initial_capital)
            final = self.equity_curve[-1]["equity"] if self.equity_curve else initial
            returns = ((final - initial) / initial) * 100
            
            # Simple max drawdown
            eqs = [e["equity"] for e in self.equity_curve]
            max_dd = 0
            if eqs:
                series = pd.Series(eqs)
                roll_max = series.expanding().max()
                drawdown = series / roll_max - 1.0
                max_dd = drawdown.min() * 100
                
            self.task.result = {
                "equity_curve": self.equity_curve,
                "metrics": {
                    "total_returns": returns,
                    "max_drawdown": max_dd,
                    "total_trades": len(self.trades)
                }
            }
            self.task.status = "completed"
            self.task.progress = 100
            self.db.commit()
            logger.info(f"Simulation completed for {self.task_id}")
            
        except Exception as e:
             self.db.rollback()
             logger.error(f"Simulation failed {self.task_id}: {str(e)}")
             self.task.status = "failed"
             self.task.error_message = str(e)
             self.db.commit()
