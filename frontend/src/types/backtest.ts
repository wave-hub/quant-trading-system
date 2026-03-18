export interface BacktestTaskBase {
    strategy_id: string;
    name: string;
    start_date: string;  // YYYY-MM-DD
    end_date: string;    // YYYY-MM-DD
    initial_capital: number;
    config?: Record<string, any>;
}

export interface BacktestTaskCreatePayload extends BacktestTaskBase {}

export interface BacktestMetrics {
    total_returns?: number;
    max_drawdown?: number;
    total_trades?: number;
}

export interface BacktestEquityPoint {
    date: string;
    equity: number;
}

export interface BacktestResult {
    equity_curve?: BacktestEquityPoint[];
    metrics?: BacktestMetrics;
}

export interface BacktestTask extends BacktestTaskBase {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    error_message?: string;
    result?: BacktestResult;
    created_at?: string;
}

export interface BacktestTrade {
    id: string;
    backtest_id: string;
    symbol: string;
    side: 'buy' | 'sell';
    quantity: number;
    price: number;
    commission?: number;
    trade_date: string;
}

export interface BacktestTaskWithTrades extends BacktestTask {
    trades: BacktestTrade[];
}

export interface BacktestListResponse {
    total: number;
    items: BacktestTask[];
}
