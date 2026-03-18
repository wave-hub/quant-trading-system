import pandas as pd
import akshare as ak
from datetime import datetime, date
from loguru import logger
from typing import List, Dict, Any, Optional

class AkShareAdapter:
    """AkShare 数据获取适配器"""

    @staticmethod
    def format_symbol_for_db(symbol: str) -> str:
        """格式化股票代码为数据库存储格式 (e.g. 000001.SZ, 600000.SH)"""
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        elif symbol.startswith("0") or symbol.startswith("3"):
            return f"{symbol}.SZ"
        elif symbol.startswith("4") or symbol.startswith("8"):
            return f"{symbol}.BJ"
        return symbol
    
    @staticmethod
    def format_symbol_for_ak(symbol: str) -> str:
        """格式化股票代码为 AkShare 接收的格式"""
        if "." in symbol:
            code, exchange = symbol.split(".")
            if exchange == "SH":
                return f"sh{code}"
            elif exchange == "SZ":
                return f"sz{code}"
            elif exchange == "BJ":
                return f"bj{code}"
        return symbol # fallback

    async def get_all_stocks(self) -> List[Dict[str, Any]]:
        """获取A股所有股票基础信息"""
        logger.info("Fetching all A-share stocks from AkShare...")
        try:
            # 基础信息
            df = ak.stock_info_a_code_name()
            # 沪深京 A 股列表
            results = []
            for _, row in df.iterrows():
                code = str(row['code'])
                name = str(row['name'])
                
                market = "UNKNOWN"
                if code.startswith("6"):
                    market = "SH"
                elif code.startswith("0") or code.startswith("3"):
                    market = "SZ"
                elif code.startswith("4") or code.startswith("8"):
                    market = "BJ"
                
                results.append({
                    "symbol": self.format_symbol_for_db(code),
                    "name": name,
                    "market": market,
                    "industry": "",  # 基础接口行业信息为空，后续可丰富
                    "list_date": None,
                    "is_hs": "N/A"
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch stock list: {str(e)}")
            raise e

    async def get_daily_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """获取某只股票的日K线历史数据（前复权）"""
        ak_symbol = self.format_symbol_for_ak(symbol)
        
        # 默认取最近一年的数据
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date.replace(year=end_date.year - 1)
            
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        logger.info(f"Fetching daily data for {symbol} from {start_str} to {end_str}")
        try:
            df = ak.stock_zh_a_hist(
                symbol=ak_symbol.replace("sh", "").replace("sz", "").replace("bj", ""), 
                period="daily", 
                start_date=start_str, 
                end_date=end_str, 
                adjust="qfq"
            )
            
            if df is None or df.empty:
                return []
                
            results = []
            for _, row in df.iterrows():
                results.append({
                    "symbol": symbol,
                    "trade_date": datetime.strptime(str(row['日期']), "%Y-%m-%d").date(),
                    "open": float(row['开盘']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "close": float(row['收盘']),
                    "volume": int(row['成交量']),
                    "amount": float(row['成交额']),
                    "adj_close": float(row['收盘']) # 由于是qfq，收盘价即为复权价
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch daily data for {symbol}: {str(e)}")
            raise e
