"""Application constants."""

from enum import Enum


class Market(str, Enum):
    """Market types."""

    A_SHARE = "a_share"
    US_STOCK = "us_stock"
    HK_STOCK = "hk_stock"


class StrategyStatus(str, Enum):
    """Strategy status."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BacktestStatus(str, Enum):
    """Backtest task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AccountType(str, Enum):
    """Account types."""

    SIMULATION = "simulation"
    REAL = "real"


class OrderSide(str, Enum):
    """Order sides."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderStatus(str, Enum):
    """Order status."""

    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class RiskSeverity(str, Enum):
    """Risk alert severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StrategyCategory(str, Enum):
    """Strategy categories."""

    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"
    STATISTICAL = "statistical"


class IndicatorCategory(str, Enum):
    """Indicator categories."""

    TREND = "trend"
    OSCILLATOR = "oscillator"
    MOMENTUM = "momentum"
    VOLUME = "volume"
    CUSTOM = "custom"


class SignalType(str, Enum):
    """Signal types."""

    ENTRY = "entry"
    EXIT = "exit"
    FILTER = "filter"


class PositionSizeMethod(str, Enum):
    """Position sizing methods."""

    FIXED = "fixed"
    PERCENTAGE = "percentage"
    KELLY = "kelly"
    VOLATILITY = "volatility"
    CUSTOM = "custom"
