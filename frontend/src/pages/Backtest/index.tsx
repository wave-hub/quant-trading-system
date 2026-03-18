import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Form, DatePicker, InputNumber, Button, Select, Table, Tag, Progress, Space, Modal, Typography } from 'antd'
import { PlayCircleOutlined, SyncOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'

import { getBacktestTasks, createBacktestTask, getBacktestTaskDetail } from '../../services/backtest'
import { getStrategies } from '../../services/strategy'
import type { BacktestTaskCreatePayload, BacktestTaskWithTrades } from '../../types/backtest'

const { RangePicker } = DatePicker
const { Title, Text } = Typography

const Backtest: React.FC = () => {
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  
  const [isDetailVisible, setIsDetailVisible] = useState(false)
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)

  // Fetch Strategies for Dropdown
  const { data: strategiesData } = useQuery({
    queryKey: ['strategies-active'],
    queryFn: () => getStrategies({ limit: 100 }),
  })

  // Fetch Backtest Tasks
  const { data: backtestsData, isLoading: isLoadingTasks, refetch: refetchTasks } = useQuery({
    queryKey: ['backtests'],
    queryFn: () => getBacktestTasks(),
  })

  // Periodically refresh if there are any running/pending tasks
  useEffect(() => {
    let interval: any
    if (backtestsData?.items?.some(t => t.status === 'running' || t.status === 'pending')) {
        interval = setInterval(() => {
            refetchTasks()
        }, 5000)
    }
    return () => clearInterval(interval)
  }, [backtestsData, refetchTasks])

  // Fetch Backtest Detail
  const { data: detailData, isFetching: isFetchingDetail } = useQuery({
    queryKey: ['backtest-detail', currentTaskId],
    queryFn: () => getBacktestTaskDetail(currentTaskId!),
    enabled: !!currentTaskId,
  })

  // Create Task Mutation
  const createMutation = useMutation({
    mutationFn: createBacktestTask,
    onSuccess: () => {
       queryClient.invalidateQueries({ queryKey: ['backtests'] })
       form.resetFields(['dateRange']) // Reset dates but keep strategy/capital preference
    }
  })

  const handleStartBacktest = (values: any) => {
    const payload: BacktestTaskCreatePayload = {
      strategy_id: values.strategy_id,
      name: `回测: ${strategiesData?.items.find(s => s.id === values.strategy_id)?.name}`,
      start_date: values.dateRange[0].format('YYYY-MM-DD'),
      end_date: values.dateRange[1].format('YYYY-MM-DD'),
      initial_capital: values.initialCapital,
      config: { commission: values.commission }
    }
    createMutation.mutate(payload)
  }

  const handleViewDetail = (id: string) => {
      setCurrentTaskId(id)
      setIsDetailVisible(true)
  }

  const columns = [
    { title: '回测名称', dataIndex: 'name', key: 'name' },
    { title: '提交时期', dataIndex: 'created_at', key: 'created_at', render: (val: string) => val ? val.split('T')[0] : '-' },
    { title: '开始日期', dataIndex: 'start_date', key: 'start_date' },
    { title: '结束日期', dataIndex: 'end_date', key: 'end_date' },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (status: string) => {
        const config: Record<string, { color: string; text: string }> = {
          completed: { color: 'green', text: '已完成' },
          running: { color: 'processing', text: '运转中' },
          failed: { color: 'red', text: '触发异常' },
          pending: { color: 'default', text: '等待中' }
        }
        return <Tag color={config[status]?.color}>{config[status]?.text}</Tag>
      }
    },
    { title: '收益率', key: 'returns',
      render: (_: any, record: any) => {
          const ret = record.result?.metrics?.total_returns
          if (ret === undefined || ret === null) return '-'
          return <span style={{ color: ret >= 0 ? '#52c41a' : '#ff4d4f' }}>{ret.toFixed(2)}%</span>
      }
    },
    { title: '最大回撤', key: 'maxDrawdown',
      render: (_: any, record: any) => {
          const dd = record.result?.metrics?.max_drawdown
          return dd !== undefined ? `${dd.toFixed(2)}%` : '-'
      }
    },
    { title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          {record.status === 'completed' && (
            <Button type="link" size="small" onClick={() => handleViewDetail(record.id)}>查看详情</Button>
          )}
          {(record.status === 'running' || record.status === 'pending') && (
            <Button type="link" size="small" icon={<SyncOutlined spin />}> {record.progress}%</Button>
          )}
          {record.status === 'failed' && (
            <Tag color="red" title={record.error_message}>异常</Tag>
          )}
        </Space>
      )
    },
  ]

  const getChartOption = (detailInfo: BacktestTaskWithTrades | undefined) => {
    if (!detailInfo?.result?.equity_curve) return {};
    
    // Convert dates and equities
    const dates = detailInfo.result.equity_curve.map((p: any) => p.date)
    const equities = detailInfo.result.equity_curve.map((p: any) => p.equity)

    // Build trade markers
    const markPointData = detailInfo.trades?.map(t => ({
        name: `${t.side.toUpperCase()} ${t.symbol}`,
        coord: [t.trade_date, detailInfo.result?.equity_curve?.find((p: any) => p.date === t.trade_date)?.equity || t.price],
        value: `${t.side === 'buy' ? '买' : '卖'}`,
        itemStyle: { color: t.side === 'buy' ? '#ffeb3b' : '#2196f3' }
    })) || []
    
    return {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value', min: 'dataMin' },
      series: [
        {
          name: '总资产 (本金+仓位)',
          type: 'line',
          data: equities,
          smooth: true,
          lineStyle: { color: '#cf1322', width: 2 },
          markPoint: {
              data: markPointData
          }
        }
      ]
    };
  }

  const activeRunningTask = backtestsData?.items?.find(t => t.status === 'running')
  const completedCount = backtestsData?.items?.filter(t => t.status === 'completed').length || 0
  const failedCount = backtestsData?.items?.filter(t => t.status === 'failed').length || 0

  return (
    <div>
      <h1>回测系统引擎</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="建立回测任务指令">
            <Form layout="vertical" form={form} onFinish={handleStartBacktest}>
              <Form.Item label="选择已有策略" name="strategy_id" rules={[{ required: true }]}>
                <Select placeholder="请选取需注入沙盒的代码或蓝图策略">
                  {strategiesData?.items?.map(s => (
                      <Select.Option key={s.id} value={s.id}>{s.name} - {s.is_visual ? '可视化' : 'Python'}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item label="回测时间范围" name="dateRange" rules={[{ required: true }]}>
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="初始资金" name="initialCapital">
                    <InputNumber style={{ width: '100%' }} min={10000} max={100000000} defaultValue={1000000} formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="手续费率" name="commission">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      max={1}
                      step={0.0001}
                      defaultValue={0.0003}
                      formatter={(value) => `${Number(value ?? 0) * 100}%`}
                      parser={(value: string | undefined) => Number(value?.replace('%', '') || 0) / 100}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item>
                <Button type="primary" htmlType="submit" icon={<PlayCircleOutlined />} loading={createMutation.isPending}>
                  提交并异步启动
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="引擎运转实时状态" style={{ marginBottom: 16, minHeight: 160 }}>
            {activeRunningTask ? (
                <>
                <Text>正在执行: {activeRunningTask.name}</Text>
                <Progress percent={activeRunningTask.progress} status="active" />
                <p style={{ textAlign: 'center', color: '#999' }}>基于高速环境计算历代行情特征库...</p>
                </>
            ) : (
                <Text type="secondary">目前资源池处于空闲待机状态。您可以分配新的探测作业。</Text>
            )}
          </Card>
          <Card title="快速统计">
            <p>总记录卷宗: <strong>{backtestsData?.total || 0}</strong> 套</p>
            <p style={{ color: '#52c41a' }}>成功终结: <strong>{completedCount}</strong> 个</p>
            <p style={{ color: '#ff4d4f' }}>异常/失败: <strong>{failedCount}</strong> 场</p>
          </Card>
        </Col>
      </Row>

      <Card title="历史记录追溯表">
        <Table columns={columns} dataSource={backtestsData?.items || []} rowKey="id" loading={isLoadingTasks} />
      </Card>

      <Modal
        title={`收益资金流水与详情诊断（ID: ${currentTaskId}）`}
        open={isDetailVisible}
        onCancel={() => setIsDetailVisible(false)}
        footer={null}
        width={1000}
        destroyOnClose
      >
          {isFetchingDetail ? <p>正在调取交易与结果记录...</p> : (
              <div>
                  <Row gutter={16} style={{ marginBottom: 16 }}>
                      <Col span={8}>
                         <Card size="small" title="总推演收益" style={{ backgroundColor: '#f6ffed' }}>
                            <Title level={4} style={{ color: '#52c41a', margin: 0 }}>
                                {detailData?.result?.metrics?.total_returns?.toFixed(2)}%
                            </Title>
                         </Card>
                      </Col>
                      <Col span={8}>
                         <Card size="small" title="最大向下折损回撤" style={{ backgroundColor: '#fff1f0' }}>
                            <Title level={4} style={{ color: '#f5222d', margin: 0 }}>
                                {detailData?.result?.metrics?.max_drawdown?.toFixed(2)}%
                            </Title>
                         </Card>
                      </Col>
                      <Col span={8}>
                         <Card size="small" title="有效交割单数" style={{ backgroundColor: '#e6f7ff' }}>
                            <Title level={4} style={{ color: '#1890ff', margin: 0 }}>
                                {detailData?.result?.metrics?.total_trades}
                            </Title>
                         </Card>
                      </Col>
                  </Row>
                  
                  <h4>资金动态变迁轨迹</h4>
                  <div style={{ height: 400, border: '1px solid #f0f0f0', padding: 8 }}>
                      <ReactECharts option={getChartOption(detailData)} style={{ height: '100%', width: '100%' }} />
                  </div>
              </div>
          )}
      </Modal>
    </div>
  )
}

export default Backtest
