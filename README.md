# 量化交易系统

## 项目介绍

一个功能完善的量化交易系统，支持从策略开发、回测验证到实盘交易的全流程。

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- SQLAlchemy - ORM
- PostgreSQL - 数据库
- Redis - 缓存和消息队列
- Celery - 任务队列
- RQAlpha - 回测引擎

### 前端
- React 18
- TypeScript
- Ant Design 5
- ECharts - 数据可视化
- Monaco Editor - 代码编辑器
- React Flow - 可视化流程图

## 项目结构

```
quant-trading-system/
├── backend/                  # 后端代码
│   ├── api/                 # API路由
│   ├── config/              # 配置文件
│   ├── core/                # 核心业务逻辑
│   │   ├── strategy/        # 策略模块
│   │   ├── data/            # 数据模块
│   │   ├── backtest/        # 回测模块
│   │   ├── trading/         # 交易模块
│   │   └── risk/            # 风控模块
│   ├── models/              # 数据库模型
│   ├── schemas/             # Pydantic模型
│   ├── services/            # 服务层
│   ├── tasks/               # Celery任务
│   └── utils/               # 工具函数
│
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── components/      # 公共组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── stores/         # 状态管理
│   │   ├── hooks/          # 自定义Hooks
│   │   ├── types/          # TypeScript类型
│   │   └── utils/          # 工具函数
│   └── package.json
│
├── strategies/              # 策略文件
├── data/                    # 数据存储
├── logs/                    # 日志
├── docker/                  # Docker配置
├── docker-compose.yml       # Docker编排
├── requirements.txt         # Python依赖
└── README.md
```

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd quant-trading-system
```

### 2. 配置环境

```bash
# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，配置数据库、Redis等
```

### 3. 使用Docker启动（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 手动启动

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 功能特性

### 策略开发
- 代码编辑器模式 - 使用Monaco Editor编写Python策略
- 可视化构建模式 - 拖拽式组件构建策略
- 策略模板库 - 预置多种策略模板

### 自定义功能
- 自定义指标 - 创建个性化技术指标
- 自定义信号 - 构建交易信号逻辑
- 自定义仓位 - 实现仓位管理算法
- 自定义风控 - 设置风控规则

### 回测系统
- 历史回测 - 基于RQAlpha的回测引擎
- 参数优化 - 网格搜索和遗传算法
- 回测报告 - 详细的分析报告

### 实盘交易
- 模拟交易 - 虚拟账户实盘模拟
- 实盘交易 - 连接券商API
- 订单管理 - 订单状态实时跟踪
- 持仓管理 - 持仓盈亏实时计算

### 风控管理
- 仓位控制 - 单仓和总仓位限制
- 止损止盈 - 固定和移动止损
- 风险监控 - 实时风险指标监控
- 告警系统 - 风险告警通知

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发计划

- [x] 阶段1: 项目初始化
- [ ] 阶段2: 数据模块
- [ ] 阶段3: 策略模块 - 代码编辑
- [ ] 阶段4: 策略模块 - 可视化构建
- [ ] 阶段5: 策略模块 - 自定义功能
- [ ] 阶段6: 回测模块
- [ ] 阶段7: 实盘交易模块
- [ ] 阶段8: 风控模块
- [ ] 阶段9: Web界面完善
- [ ] 阶段10: 测试与优化
- [ ] 阶段11: 部署与文档

## 许可证

MIT License
