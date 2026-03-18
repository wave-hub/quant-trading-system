from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from loguru import logger
import pandas as pd

from backend.models.market import Stock, MarketData
from backend.core.data.adapters.akshare_adapter import AkShareAdapter

class DataService:
    def __init__(self, db: Session):
        self.db = db
        self.adapter = AkShareAdapter()
        
    async def get_stocks(self, skip: int = 0, limit: int = 100) -> dict:
        """获取本地数据库中的股票列表"""
        stmt = select(Stock).offset(skip).limit(limit)
        result = self.db.execute(stmt)
        stocks = result.scalars().all()
        
        count_stmt = select(Stock.id)
        total = len(self.db.execute(count_stmt).fetchall())
        
        return {
            "total": total,
            "items": stocks
        }
        
    async def get_market_data(self, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        """获取本地数据库中的市场数据"""
        stmt = select(MarketData).where(MarketData.symbol == symbol).order_by(MarketData.trade_date.asc())
        if start_date:
            stmt = stmt.where(MarketData.trade_date >= start_date)
        if end_date:
            stmt = stmt.where(MarketData.trade_date <= end_date)
            
        result = self.db.execute(stmt)
        data = result.scalars().all()
        
        # Convert to dictionary and calculate MA using pandas
        dict_data = [
            {
                "id": str(item.id),
                "symbol": item.symbol,
                "trade_date": item.trade_date,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
                "volume": item.volume,
                "amount": item.amount,
                "adj_close": item.adj_close,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            }
            for item in data
        ]
        
        if dict_data:
            df = pd.DataFrame(dict_data)
            df.set_index("trade_date", inplace=True)
            df.sort_index(inplace=True)
            
            # Simple Moving Averages
            df["ma5"] = df["close"].rolling(window=5, min_periods=1).mean()
            df["ma20"] = df["close"].rolling(window=20, min_periods=1).mean()
            
            # Reconstruct list of dicts, keeping original structure + moving averages
            df.reset_index(inplace=True)
            dict_data = df.to_dict(orient="records")
            
            # Fix date serialization issue from pandas back to dict
            for item in dict_data:
                item["ma5"] = round(item["ma5"], 3) if pd.notna(item["ma5"]) else None
                item["ma20"] = round(item["ma20"], 3) if pd.notna(item["ma20"]) else None
        
        return {
            "total": len(dict_data),
            "items": dict_data
        }

    async def sync_stocks(self) -> int:
        """同步全量股票列表到数据库"""
        try:
            stocks_data = await self.adapter.get_all_stocks()
            logger.info(f"Fetched {len(stocks_data)} stocks from AkShare.")
            
            # 由于全市场股票较多，这里可以进行批量 upsert，但为了简单起见，这里演示按需插入/更新
            inserted_count = 0
            for item in stocks_data:
                stmt = select(Stock).where(Stock.symbol == item["symbol"])
                existing_stock = self.db.execute(stmt).scalar_one_or_none()
                
                if not existing_stock:
                    new_stock = Stock(**item)
                    self.db.add(new_stock)
                    inserted_count += 1
                else:
                    existing_stock.name = item["name"]
                    existing_stock.market = item["market"]
                    
            self.db.commit()
            return len(stocks_data)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing stocks: {str(e)}")
            raise e
            
    async def sync_market_data(self, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
        """同步单只股票的历史数据"""
        try:
            market_data = await self.adapter.get_daily_data(symbol, start_date, end_date)
            logger.info(f"Fetched {len(market_data)} records for {symbol} from AkShare.")
            
            inserted_count = 0
            for item in market_data:
                stmt = select(MarketData).where(
                    MarketData.symbol == item["symbol"],
                    MarketData.trade_date == item["trade_date"]
                )
                existing_data = self.db.execute(stmt).scalar_one_or_none()
                
                if not existing_data:
                    new_data = MarketData(**item)
                    self.db.add(new_data)
                    inserted_count += 1
                else:
                    existing_data.open = item["open"]
                    existing_data.high = item["high"]
                    existing_data.low = item["low"]
                    existing_data.close = item["close"]
                    existing_data.volume = item["volume"]
                    existing_data.amount = item["amount"]
                    existing_data.adj_close = item["adj_close"]
                    
            self.db.commit()
            return len(market_data)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing market data for {symbol}: {str(e)}")
            raise e
