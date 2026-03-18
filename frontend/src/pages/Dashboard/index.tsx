import React from 'react'
import { Card, Row, Col, Statistic, Table } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, WalletOutlined, SwapOutlined, AlertOutlined } from '@ant-design/icons'

const Dashboard: React.FC = () => {
  const todayPnL = 25680.32
  const recentTrades = [
    { key: '1', symbol: '600519', name: '贵州茅台', side: '买入', quantity: 100, price: 1850.5, time: '2026-02-21 10:30:00' },
    { key: '2', symbol: '000858', name: '五粮液', side: '卖出', quantity: 200, price: 168.2, time: '2026-02-21 10:15:00' },
    { key: '3', symbol: '600036', name: '招商银行', side: '买入', quantity: 500, price: 42.8, time: '2026-02-21 09:45:00' },
  ]

  const columns = [
    { title: '股票代码', dataIndex: 'symbol', key: 'symbol' },
    { title: '股票名称', dataIndex: 'name', key: 'name' },
    { title: '方向', dataIndex: 'side', key: 'side', 
      render: (side: string) => (
        <span style={{ color: side === '买入' ? '#52c41a' : '#ff4d4f' }}>{side}</span>
      )
    },
    { title: '数量', dataIndex: 'quantity', key: 'quantity' },
    { title: '价格', dataIndex: 'price', key: 'price' },
    { title: '时间', dataIndex: 'time', key: 'time' },
  ]

  return (
    <div>
      <h1>仪表盘</h1>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="账户总资产"
              value={1128930.56}
              precision={2}
              prefix={<WalletOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日收益"
              value={todayPnL}
              precision={2}
              prefix={todayPnL >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix="元"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="持仓数量"
              value={8}
              suffix="只"
              prefix={<SwapOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="风险等级"
              value="中"
              prefix={<AlertOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="账户收益情况" style={{ height: '100%' }}>
            <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
              收益曲线图表区域
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="资产分布" style={{ height: '100%' }}>
            <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
              持仓分布饼图区域
            </div>
          </Card>
        </Col>
      </Row>

      <Card title="最近交易">
        <Table columns={columns} dataSource={recentTrades} pagination={false} size="small" />
      </Card>
    </div>
  )
}

export default Dashboard
