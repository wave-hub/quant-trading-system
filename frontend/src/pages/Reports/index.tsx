import React from 'react'
import { Card, Row, Col, Table, Button, DatePicker, Space } from 'antd'
import { DownloadOutlined, FileTextOutlined } from '@ant-design/icons'

const { RangePicker } = DatePicker

const Reports: React.FC = () => {
  const reports = [
    { key: '1', type: '日报', date: '2026-02-21', account: '模拟账户', returns: 2.35, trades: 5, status: '已生成' },
    { key: '2', type: '周报', date: '2026-02-14', account: '模拟账户', returns: 8.56, trades: 28, status: '已生成' },
    { key: '3', type: '月报', date: '2026-01-31', account: '模拟账户', returns: 15.23, trades: 120, status: '已生成' },
    { key: '4', type: '季报', date: '2025-12-31', account: '模拟账户', returns: 32.18, trades: 380, status: '已生成' },
    { key: '5', type: '年报', date: '2025-12-31', account: '模拟账户', returns: 45.67, trades: 1560, status: '已生成' },
  ]

  const columns = [
    { title: '报告类型', dataIndex: 'type', key: 'type',
      render: (type: string) => (
        <span>
          <FileTextOutlined style={{ marginRight: 8 }} />
          {type}
        </span>
      )
    },
    { title: '日期', dataIndex: 'date', key: 'date' },
    { title: '账户', dataIndex: 'account', key: 'account' },
    { title: '收益率', dataIndex: 'returns', key: 'returns',
      render: (v: number) => <span style={{ color: v >= 0 ? '#52c41a' : '#ff4d4f' }}>{v >= 0 ? '+' : ''}{v.toFixed(2)}%</span>
    },
    { title: '交易次数', dataIndex: 'trades', key: 'trades' },
    { title: '状态', dataIndex: 'status', key: 'status' },
    { title: '操作', key: 'action',
      render: () => (
        <Button type="link" size="small" icon={<DownloadOutlined />}>下载</Button>
      )
    },
  ]

  return (
    <div>
      <h1>报告中心</h1>
      
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <RangePicker />
          <Button type="primary">查询</Button>
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 14, color: '#999' }}>本月收益率</div>
              <div style={{ fontSize: 32, color: '#52c41a', fontWeight: 'bold' }}>+15.23%</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 14, color: '#999' }}>本年收益率</div>
              <div style={{ fontSize: 32, color: '#52c41a', fontWeight: 'bold' }}>+45.67%</div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 14, color: '#999' }}>累计交易</div>
              <div style={{ fontSize: 32, fontWeight: 'bold' }}>1,560</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Card title="报告列表">
        <Table columns={columns} dataSource={reports} rowKey="key" />
      </Card>
    </div>
  )
}

export default Reports
