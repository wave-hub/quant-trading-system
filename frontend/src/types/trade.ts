export interface TradeAccount {
    id: string;
    name: string;
    account_type: 'simulation' | 'real';
    broker?: string;
    account_number?: string;
    initial_capital: number;
    current_capital: number;
    status: 'active' | 'inactive';
}

export interface TradePosition {
    id: string;
    account_id: string;
    symbol: string;
    quantity: number;
    avg_price?: number;
    market_price?: number;
    market_value?: number;
    profit_loss?: number;
}

export interface TradeOrder {
    id: string;
    order_id: string;
    account_id: string;
    symbol: string;
    side: 'buy' | 'sell';
    order_type: 'market' | 'limit';
    quantity: number;
    price?: number;
    status: 'pending' | 'filled' | 'cancelled' | 'failed' | 'error';
    filled_quantity: number;
    avg_fill_price?: number;
    created_at?: string;
}

export interface TradeAccountSummary extends TradeAccount {
    positions: TradePosition[];
    orders: TradeOrder[];
}

export interface TradeOrderPayload {
    account_id: string;
    symbol: string;
    side: 'buy' | 'sell';
    order_type: 'market' | 'limit';
    quantity: number;
    price?: number;
}

/** 资金划拨请求 */
export interface FundPayload {
    action: 'deposit' | 'withdraw';
    amount: number;
}

/** 资金划拨结果 */
export interface FundResult {
    message: string;
    action: string;
    amount: number;
    balance_before: number;
    balance_after: number;
}

