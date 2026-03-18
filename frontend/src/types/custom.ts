export interface CustomComponentBase {
    id: string;
    name: string;
    description?: string;
    category?: string;
    is_public: boolean;
    author_id: string;
    usage_count: number;
    created_at?: string;
    updated_at?: string;
}

export interface CustomIndicator extends CustomComponentBase {
    formula: string;
    parameters: Record<string, any>;
}

export interface CustomIndicatorCreatePayload {
    name: string;
    description?: string;
    category?: string;
    is_public?: boolean;
    formula: string;
    parameters?: Record<string, any>;
}

export interface CustomSignal extends CustomComponentBase {
    conditions: Record<string, any>;
    indicators?: Record<string, any>;
}

export interface CustomSignalCreatePayload {
    name: string;
    description?: string;
    category?: string;
    is_public?: boolean;
    conditions: Record<string, any>;
    indicators?: Record<string, any>;
}

export interface CustomPosition extends CustomComponentBase {
    algorithm: string;
    parameters: Record<string, any>;
}

export interface CustomPositionCreatePayload {
    name: string;
    description?: string;
    category?: string;
    is_public?: boolean;
    algorithm: string;
    parameters?: Record<string, any>;
}

export interface CustomRiskRule extends CustomComponentBase {
    rule_config: Record<string, any>;
    rule_type?: string;
    severity?: string;
}

export interface CustomRiskRuleCreatePayload {
    name: string;
    description?: string;
    category?: string;
    is_public?: boolean;
    rule_config: Record<string, any>;
    rule_type?: string;
    severity?: string;
}

export interface CustomComponentListResponse<T> {
    total: number;
    items: T[];
}
