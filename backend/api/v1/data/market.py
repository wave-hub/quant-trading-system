from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from backend.config.database import get_db
from backend.services.data import DataService
from backend.schemas.data import StockListResponse, MarketDataListResponse

router = APIRouter()

# NOTE: 筛选展示的核心大盘指数代码列表
CORE_INDEX_CODES = [
    "上证指数", "深证成指", "创业板指", "科创50",
    "沪深300", "中证500", "中证1000", "上证50",
]


@router.get("/stocks", response_model=StockListResponse)
async def get_stocks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取所有股票列表（从本地数据库）"""
    data_service = DataService(db)
    return await data_service.get_stocks(skip=skip, limit=limit)

@router.get("/history", response_model=MarketDataListResponse)
async def get_market_data(
    symbol: str = Query(..., description="股票代码, 如 000001.SZ"),
    start_date: Optional[date] = Query(None, description="开始日期, 格式 YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="结束日期, 格式 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取指定股票的历史行情数据（从本地数据库）"""
    data_service = DataService(db)
    return await data_service.get_market_data(
        symbol=symbol, start_date=start_date, end_date=end_date
    )

@router.get("/indices")
async def get_indices():
    """
    获取 A 股核心大盘指数实时行情
    数据来源：akshare stock_zh_index_spot_em
    """
    try:
        import os
        import urllib.request
        import akshare as ak

        # NOTE: macOS 系统代理(如 Clash)会通过 urllib.request.getproxies() 返回
        # 这会导致 requests 库自动走代理，东方财富 API 无法通过代理访问
        # 采用多重手段确保请求直连：
        # 1. 设置 NO_PROXY=* 告诉 requests 跳过所有代理
        # 2. 临时替换 getproxies 返回空字典
        # 3. 清除所有代理环境变量
        proxy_env_keys = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',
                          'all_proxy', 'ALL_PROXY']
        saved_env = {k: os.environ.pop(k) for k in proxy_env_keys if k in os.environ}
        os.environ['NO_PROXY'] = '*'
        os.environ['no_proxy'] = '*'

        # HACK: 临时替换 urllib 的代理探测函数
        original_getproxies = urllib.request.getproxies
        urllib.request.getproxies = lambda: {}

        try:
            df = ak.stock_zh_index_spot_em()
        finally:
            urllib.request.getproxies = original_getproxies
            os.environ.pop('NO_PROXY', None)
            os.environ.pop('no_proxy', None)
            os.environ.update(saved_env)

        # 筛选核心指数
        core_df = df[df["名称"].isin(CORE_INDEX_CODES)]

        result = []
        for _, row in core_df.iterrows():
            result.append({
                "code": str(row.get("代码", "")),
                "name": str(row.get("名称", "")),
                "latest_price": float(row.get("最新价", 0)),
                "change_amount": float(row.get("涨跌额", 0)),
                "change_percent": float(row.get("涨跌幅", 0)),
                "volume": float(row.get("成交量", 0)),
                "turnover": float(row.get("成交额", 0)),
                "open_price": float(row.get("今开", 0)),
                "high_price": float(row.get("最高", 0)),
                "low_price": float(row.get("最低", 0)),
                "prev_close": float(row.get("昨收", 0)),
            })

        return {"items": result, "total": len(result)}

    except ImportError:
        logger.error("akshare 未安装，无法获取大盘指数数据")
        raise HTTPException(status_code=500, detail="akshare 依赖未安装")
    except Exception as e:
        logger.error(f"获取大盘指数数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取大盘指数数据失败: {str(e)}")


@router.post("/sync/stocks")
async def sync_stocks(db: Session = Depends(get_db)):
    """手动触发同步全A股股票基础信息到本地数据库"""
    data_service = DataService(db)
    try:
        count = await data_service.sync_stocks()
        return {"message": "success", "synced_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/history")
async def sync_history(
    symbol: str = Query(..., description="股票代码, 如 000001.SZ"),
    start_date: Optional[date] = Query(None, description="开始日期, 格式 YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="结束日期, 格式 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """手动触发同步单只股票的历史数据到本地数据库"""
    data_service = DataService(db)
    try:
        count = await data_service.sync_market_data(
            symbol=symbol, start_date=start_date, end_date=end_date
        )
        return {"message": "success", "synced_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
