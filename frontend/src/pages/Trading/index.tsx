import React, { useState, useEffect } from 'react'
import {
  Card, Row, Col, Table, Button, Tag, Statistic, Form,
  Input, Select, InputNumber, message, Space, Modal, Radio
} from 'antd'
import {
  RocketOutlined,
  DollarOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { getAccounts, getAccountSummary, placeOrder, fundAccount } from '../../services/trade'
import type { TradeOrderPayload, FundPayload } from '../../types/trade'

const { Option } = Select

const Trading: React.FC = () => {
  const [form] = Form.useForm()
  const [fundForm] = Form.useForm()
  const queryClient = useQueryClient()
  
  const [activeAccountId, setActiveAccountId] = useState<string | null>(null)
  const [fundModalOpen, setFundModalOpen] = useState(false)
  const [fundTargetAccountId, setFundTargetAccountId] = useState<string | null>(null)

  // 1. 获取用户账户集合
  const { data: accountsData, isLoading: isLoadingAccounts } = useQuery({
    queryKey: ['trade-accounts'],
    queryFn: getAccounts,
  })

  // Set default active account if none selected
  useEffect(() => {
     if (accountsData && accountsData.length > 0 && !activeAccountId) {
         setActiveAccountId(accountsData[0].id)
     }
  }, [accountsData, activeAccountId])

  // 2. 根据激活的 AccountId 拿细节流水 (轮询)
  const { data: accountDetail, isFetching: isFetchingDetail } = useQuery({
    queryKey: ['trade-account-detail', activeAccountId],
    queryFn: () => getAccountSummary(activeAccountId!),
    enabled: !!activeAccountId,
    refetchInterval: 5000 // 5s 轮询刷新实盘持仓
  })

  // 3. 提交订单
  const orderMutation = useMutation({
    mutationFn: placeOrder,
    onSuccess: () => {
       message.success('指令已送达并尝试撮合')
       form.resetFields()
       queryClient.invalidateQueries({ queryKey: ['trade-account-detail', activeAccountId] })
    },
    onError: (err: any) => {
       message.error(err.response?.data?.detail || '下单被拒！')
    }
  })

  // 4. 资金划拨
  const fundMutation = useMutation({
    mutationFn: (params: { accountId: string; payload: FundPayload }) =>
      fundAccount(params.accountId, params.payload),
    onSuccess: (result) => {
      message.success(`${result.message}！操作后余额：¥${result.balance_after.toLocaleString()}`)
      setFundModalOpen(false)
      fundForm.resetFields()
      // 刷新账户列表和当前账户详情
      queryClient.invalidateQueries({ queryKey: ['trade-accounts'] })
      queryClient.invalidateQueries({ queryKey: ['trade-account-detail'] })
    },
    onError: (err: any) => {
      message.error(err.response?.data?.detail || '资金划拨失败')
    },
  })

  const onPlaceOrder = (values: any) => {
      if (!activeAccountId) return
      const payload: TradeOrderPayload = {
          account_id: activeAccountId,
          symbol: values.symbol,
          side: values.side,
          order_type: values.order_type,
          quantity: values.quantity,
          price: values.price
      }
      orderMutation.mutate(payload)
  }

  /** 打开资金划拨弹窗 */
  const openFundModal = (accountId: string) => {
    setFundTargetAccountId(accountId)
    setFundModalOpen(true)
    fundForm.resetFields()
  }

  /** 提交资金划拨 */
  const onFundSubmit = (values: { action: 'deposit' | 'withdraw'; amount: number }) => {
    if (!fundTargetAccountId) return
    fundMutation.mutate({
      accountId: fundTargetAccountId,
      payload: { action: values.action, amount: values.amount },
    })
  }

  const accountColumns = [
    { title: '账户名称', dataIndex: 'name', key: 'name' },
    { title: '类型', dataIndex: 'account_type', key: 'type',
      render: (type: string) => <Tag color={type === 'simulation' ? 'blue' : 'red'}>{type === 'simulation' ? '模拟' : '实盘'}</Tag>
    },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (status: string) => <Tag color={status === 'active' ? 'green' : 'default'}>{status === 'active' ? '运行中' : '已停止'}</Tag>
    },
    { title: '可用资金', dataIndex: 'current_capital', key: 'current_capital', render: (v: number) => v ? `¥${v.toLocaleString()}` : '¥0' },
    { title: '初始本金', dataIndex: 'initial_capital', key: 'initial_capital', render: (v: number) => v ? `¥${v.toLocaleString()}` : '¥0' },
    { title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
           {record.id === activeAccountId && <Tag color="gold">关注中</Tag>}
           <Button type="link" size="small" onClick={() => setActiveAccountId(record.id)}>切换看板</Button>
           <Button
             type="link"
             size="small"
             icon={<DollarOutlined />}
             onClick={() => openFundModal(record.id)}
             style={{ color: '#fa8c16' }}
           >
             资金划拨
           </Button>
        </Space>
      )
    },
  ]

  const positionColumns = [
    { title: '股票代码', dataIndex: 'symbol', key: 'symbol' },
    { title: '持仓数量', dataIndex: 'quantity', key: 'quantity' },
    { title: '持仓成本', dataIndex: 'avg_price', key: 'avg_price', render: (v: number) => v ? v.toFixed(2) : '-' },
  ]

  const orderColumns = [
    { title: '时间', dataIndex: 'created_at', key: 'created_at', render: (v: string) => v ? v.split('.')[0].replace('T', ' ') : '-' },
    { title: '内部号', dataIndex: 'order_id', key: 'order_id' },
    { title: '标的', dataIndex: 'symbol', key: 'symbol' },
    { title: '方向', dataIndex: 'side', key: 'side',
      render: (v: string) => <Tag color={v === 'buy' ? 'red' : 'green'}>{v === 'buy' ? '买入' : '卖出'}</Tag>
    },
    { title: '类型', dataIndex: 'order_type', key: 'order_type',
      render: (v: string) => v === 'market' ? '市价单' : '限价单' 
    },
    { title: '数量', dataIndex: 'quantity', key: 'quantity' },
    { title: '成交均价', dataIndex: 'avg_fill_price', key: 'avg_fill_price', render: (v: number | undefined) => v ? v.toFixed(3) : '-' },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (v: string) => {
        const config: Record<string, { color: string; text: string }> = {
          filled: { color: 'green', text: '已成' },
          pending: { color: 'orange', text: '挂单中' },
          cancelled: { color: 'default', text: '已撤' },
          failed: { color: 'red', text: '废单/资金不足' },
          error: { color: 'red', text: '系统异常' }
        }
        return <Tag color={config[v]?.color}>{config[v]?.text}</Tag>
      }
    },
  ]

  return (
    <div>
      <h1>实盘交易</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="模拟盘/实盘 总可用余资" value={accountDetail?.current_capital || 0} prefix="¥" precision={2} loading={isFetchingDetail} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="当前策略数映射" value={0} prefix="🤖" />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="持仓结构数 (Positions)" value={accountDetail?.positions?.length || 0} prefix="🎯" loading={isFetchingDetail} />
          </Card>
        </Col>
      </Row>

      <Card title="总账户矩阵" style={{ marginBottom: 24 }}>
        <Table columns={accountColumns} dataSource={accountsData || []} rowKey="id" pagination={false} size="small" loading={isLoadingAccounts} />
      </Card>
      
      <Card title="[沙盒支持] 极速网关打单 / Paper Trading Mock" style={{ marginBottom: 24, backgroundColor: '#f0f5ff' }}>
         <Form form={form} layout="inline" onFinish={onPlaceOrder}>
            <Form.Item name="symbol" rules={[{ required: true, message: '输入如 000001.SZ' }]}>
               <Input placeholder="交易标的代号" style={{ width: 140 }} />
            </Form.Item>
            <Form.Item name="side" rules={[{ required: true }]} initialValue="buy">
               <Select style={{ width: 100 }}>
                   <Option value="buy">买入 (Buy)</Option>
                   <Option value="sell">卖出 (Sell)</Option>
               </Select>
            </Form.Item>
            <Form.Item name="order_type" rules={[{ required: true }]} initialValue="market">
               <Select style={{ width: 120 }}>
                   <Option value="market">市价单 (Market)</Option>
                   <Option value="limit">限价单 (Limit)</Option>
               </Select>
            </Form.Item>
            <Form.Item name="quantity" rules={[{ required: true }]}>
               <InputNumber placeholder="股数" min={1} style={{ width: 100 }} />
            </Form.Item>
            <Form.Item name="price">
               <InputNumber placeholder="限价(若市价留空)" min={0.01} step={0.01} style={{ width: 140 }} />
            </Form.Item>
            <Form.Item>
               <Button type="primary" htmlType="submit" icon={<RocketOutlined />} loading={orderMutation.isPending}>发射订单</Button>
            </Form.Item>
         </Form>
      </Card>

      <Row gutter={16}>
          <Col span={12}>
              <Card title={`实盘持仓快照 (${accountDetail?.name || '-'})`}>
                <Table columns={positionColumns} dataSource={accountDetail?.positions || []} rowKey="id" pagination={false} size="small" loading={isFetchingDetail} />
              </Card>
          </Col>
          <Col span={12}>
              <Card title="实盘委笔流水记录">
                <Table columns={orderColumns} dataSource={accountDetail?.orders || []} rowKey="id" pagination={{ pageSize: 5 }} size="small" loading={isFetchingDetail} />
              </Card>
          </Col>
      </Row>

      {/* 资金划拨弹窗 */}
      <Modal
        title={
          <span>
            <DollarOutlined style={{ color: '#fa8c16', marginRight: 8 }} />
            资金划拨（充值 / 提现）
          </span>
        }
        open={fundModalOpen}
        onCancel={() => setFundModalOpen(false)}
        footer={null}
        destroyOnClose
        width={460}
      >
        <Form
          form={fundForm}
          layout="vertical"
          onFinish={onFundSubmit}
          initialValues={{ action: 'deposit' }}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            name="action"
            label="操作类型"
            rules={[{ required: true }]}
          >
            <Radio.Group buttonStyle="solid" style={{ width: '100%' }}>
              <Radio.Button value="deposit" style={{ width: '50%', textAlign: 'center' }}>
                <ArrowDownOutlined style={{ color: '#cf1322' }} /> 充值（入金）
              </Radio.Button>
              <Radio.Button value="withdraw" style={{ width: '50%', textAlign: 'center' }}>
                <ArrowUpOutlined style={{ color: '#3f8600' }} /> 提现（出金）
              </Radio.Button>
            </Radio.Group>
          </Form.Item>

          <Form.Item
            name="amount"
            label="金额（元）"
            rules={[
              { required: true, message: '请输入金额' },
              { type: 'number', min: 0.01, message: '金额必须大于 0' },
            ]}
          >
            <InputNumber
              placeholder="请输入操作金额"
              prefix="¥"
              min={0.01}
              step={1000}
              style={{ width: '100%' }}
              size="large"
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setFundModalOpen(false)}>取消</Button>
              <Button
                type="primary"
                htmlType="submit"
                icon={<DollarOutlined />}
                loading={fundMutation.isPending}
                style={{ backgroundColor: '#fa8c16', borderColor: '#fa8c16' }}
              >
                确认划拨
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Trading
