import React from 'react'
import { Card, Row, Col, Table, Tag, Spin, Statistic, Typography } from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  StockOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { getIndices } from '../../services/market'
import type { IndexData } from '../../types/market'

const { Title } = Typography

/**
 * 格式化大数字为亿/万单位
 * @param value 原始数值
 * @returns 格式化后的字符串
 */
const formatLargeNumber = (value: number): string => {
  if (value >= 1e8) return `${(value / 1e8).toFixed(2)} 亿`
  if (value >= 1e4) return `${(value / 1e4).toFixed(2)} 万`
  return value.toLocaleString()
}

/** 核心指数卡片：展示单个指数的实时行情概要 */
const IndexCard: React.FC<{ item: IndexData }> = ({ item }) => {
  const isUp = item.change_amount >= 0
  const color = isUp ? '#cf1322' : '#3f8600'
  const bgGradient = isUp
    ? 'linear-gradient(135deg, #fff1f0 0%, #fff 100%)'
    : 'linear-gradient(135deg, #f6ffed 0%, #fff 100%)'

  return (
    <Card
      hoverable
      style={{
        background: bgGradient,
        borderLeft: `4px solid ${color}`,
        borderRadius: 8,
      }}
      styles={{ body: { padding: '16px 20px' } }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 15, fontWeight: 600, color: '#333' }}>
          <StockOutlined style={{ marginRight: 6, color }} />
          {item.name}
        </span>
        <Tag color={isUp ? 'red' : 'green'} style={{ margin: 0, fontWeight: 500 }}>
          {item.code}
        </Tag>
      </div>

      <Statistic
        value={item.latest_price}
        precision={2}
        valueStyle={{ color, fontSize: 28, fontWeight: 700 }}
      />

      <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
        <span style={{ color, fontSize: 14 }}>
          {isUp ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {' '}{isUp ? '+' : ''}{item.change_amount.toFixed(2)}
        </span>
        <span style={{ color, fontSize: 14, fontWeight: 500 }}>
          {isUp ? '+' : ''}{item.change_percent.toFixed(2)}%
        </span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, color: '#888', fontSize: 12 }}>
        <span>成交额: {formatLargeNumber(item.turnover)}</span>
        <span>昨收: {item.prev_close.toFixed(2)}</span>
      </div>
    </Card>
  )
}

const Market: React.FC = () => {
  const { data: indicesData, isLoading, isError, refetch } = useQuery({
    queryKey: ['market-indices'],
    queryFn: getIndices,
    // NOTE: 大盘数据每30秒自动刷新一次
    refetchInterval: 30_000,
  })

  const columns = [
    {
      title: '代码', dataIndex: 'code', key: 'code', width: 100,
      render: (v: string) => <Tag>{v}</Tag>,
    },
    {
      title: '名称', dataIndex: 'name', key: 'name', width: 120,
      render: (v: string) => <span style={{ fontWeight: 500 }}>{v}</span>,
    },
    {
      title: '最新价', dataIndex: 'latest_price', key: 'latest_price', width: 120,
      render: (v: number, record: IndexData) => (
        <span style={{ color: record.change_amount >= 0 ? '#cf1322' : '#3f8600', fontWeight: 600 }}>
          {v.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌额', dataIndex: 'change_amount', key: 'change_amount', width: 100,
      render: (v: number) => (
        <span style={{ color: v >= 0 ? '#cf1322' : '#3f8600' }}>
          {v >= 0 ? '+' : ''}{v.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌幅', dataIndex: 'change_percent', key: 'change_percent', width: 100,
      render: (v: number) => (
        <Tag color={v >= 0 ? 'red' : 'green'} style={{ fontWeight: 500 }}>
          {v >= 0 ? '+' : ''}{v.toFixed(2)}%
        </Tag>
      ),
    },
    {
      title: '今开', dataIndex: 'open_price', key: 'open_price', width: 100,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '最高', dataIndex: 'high_price', key: 'high_price', width: 100,
      render: (v: number) => <span style={{ color: '#cf1322' }}>{v.toFixed(2)}</span>,
    },
    {
      title: '最低', dataIndex: 'low_price', key: 'low_price', width: 100,
      render: (v: number) => <span style={{ color: '#3f8600' }}>{v.toFixed(2)}</span>,
    },
    {
      title: '昨收', dataIndex: 'prev_close', key: 'prev_close', width: 100,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '成交额', dataIndex: 'turnover', key: 'turnover', width: 120,
      render: (v: number) => formatLargeNumber(v),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <Title level={3} style={{ margin: 0 }}>
          <StockOutlined style={{ marginRight: 8 }} />
          大盘浏览
        </Title>
        <a onClick={() => refetch()} style={{ fontSize: 14 }}>
          <ReloadOutlined style={{ marginRight: 4 }} />
          刷新数据
        </a>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 80 }}>
          <Spin size="large" tip="正在获取大盘行情数据..." />
        </div>
      ) : isError ? (
        <Card style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: '#ff4d4f', fontSize: 16 }}>获取大盘数据失败，请检查后端服务或网络连接</p>
          <a onClick={() => refetch()}>点击重试</a>
        </Card>
      ) : (
        <>
          {/* 核心指数卡片区域 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            {indicesData?.items?.slice(0, 8).map((item) => (
              <Col xs={24} sm={12} md={8} lg={6} key={item.code}>
                <IndexCard item={item} />
              </Col>
            ))}
          </Row>

          {/* 完整指数表格 */}
          <Card title="核心指数明细表" style={{ borderRadius: 8 }}>
            <Table
              columns={columns}
              dataSource={indicesData?.items || []}
              rowKey="code"
              pagination={false}
              size="middle"
              scroll={{ x: 1000 }}
            />
          </Card>
        </>
      )}
    </div>
  )
}

export default Market
