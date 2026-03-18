import React, { useEffect, useMemo, useState } from 'react'
import {
  Badge,
  Button,
  Card,
  Col,
  Descriptions,
  Drawer,
  Form,
  Input,
  List,
  Modal,
  Row,
  Select,
  Space,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from 'antd'
import { PlusOutlined, ReloadOutlined, ArrowRightOutlined } from '@ant-design/icons'
import ReactFlow, { Background, Controls, Edge, Node } from 'reactflow'
import 'reactflow/dist/style.css'

import {
  RiskEvent,
  RiskEventDetail,
  addRiskDecision,
  addRiskMeasure,
  createRiskEvent,
  getRiskEventDetail,
  listRiskEvents,
  transitionRiskEvent,
} from '@/services/risk'

const { Text } = Typography

type StepKey = 'step1_detected' | 'step2_assess_decide' | 'step3_execute_measures' | 'step4_follow_up'

const stepMeta: Record<StepKey, { title: string; hint: string }> = {
  step1_detected: { title: 'Step1 发现/上报', hint: '交易员/风控专员发现风险事件并汇报' },
  step2_assess_decide: { title: 'Step2 评估/决策', hint: '召开风控/投决会，评估影响并确定措施' },
  step3_execute_measures: { title: 'Step3 执行措施', hint: '落实风控措施，跟踪执行进展与效果' },
  step4_follow_up: { title: 'Step4 优化复盘', hint: '复盘优化流程，沉淀规则以预防同类风险' },
}

function stepTag(step: string) {
  const map: Record<string, { color: string; text: string }> = {
    step1_detected: { color: 'default', text: 'Step1' },
    step2_assess_decide: { color: 'processing', text: 'Step2' },
    step3_execute_measures: { color: 'warning', text: 'Step3' },
    step4_follow_up: { color: 'success', text: 'Step4' },
  }
  const x = map[step] || { color: 'default', text: step }
  return <Tag color={x.color}>{x.text}</Tag>
}

function statusBadge(status: string) {
  const map: Record<string, { status: any; text: string }> = {
    open: { status: 'default', text: '开放' },
    in_progress: { status: 'processing', text: '处理中' },
    resolved: { status: 'success', text: '已解决' },
    closed: { status: 'warning', text: '已关闭' },
  }
  const x = map[status] || { status: 'default', text: status }
  return <Badge status={x.status} text={x.text} />
}

function buildFlow(currentStep?: string) {
  const steps: StepKey[] = ['step1_detected', 'step2_assess_decide', 'step3_execute_measures', 'step4_follow_up']
  const activeIdx = currentStep ? steps.indexOf(currentStep as StepKey) : -1

  const nodes: Node[] = steps.map((s, i) => {
    const isActive = i === activeIdx
    const isDone = activeIdx >= 0 && i < activeIdx
    const bg = isActive ? '#e6f4ff' : isDone ? '#f6ffed' : '#fff'
    const border = isActive ? '#1677ff' : isDone ? '#52c41a' : '#d9d9d9'
    return {
      id: s,
      position: { x: i * 230, y: 0 },
      data: {
        label: (
          <div style={{ width: 210 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text strong>{stepMeta[s].title}</Text>
              {isActive ? <Tag color="blue">当前</Tag> : isDone ? <Tag color="green">完成</Tag> : <Tag>待办</Tag>}
            </div>
            <div style={{ marginTop: 6, color: '#666', fontSize: 12, lineHeight: 1.4 }}>{stepMeta[s].hint}</div>
          </div>
        ),
      },
      style: {
        padding: 10,
        borderRadius: 10,
        border: `1px solid ${border}`,
        background: bg,
        boxShadow: isActive ? '0 6px 18px rgba(22,119,255,0.15)' : undefined,
      },
    }
  })

  const edges: Edge[] = [
    { id: 'e1-2', source: 'step1_detected', target: 'step2_assess_decide', animated: true },
    { id: 'e2-3', source: 'step2_assess_decide', target: 'step3_execute_measures', animated: true },
    { id: 'e3-4', source: 'step3_execute_measures', target: 'step4_follow_up', animated: true },
  ]

  return { nodes, edges }
}

const Risk: React.FC = () => {
  const [events, setEvents] = useState<RiskEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<RiskEventDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)

  const [createOpen, setCreateOpen] = useState(false)
  const [decisionOpen, setDecisionOpen] = useState(false)
  const [measureOpen, setMeasureOpen] = useState(false)
  const [transitionOpen, setTransitionOpen] = useState(false)

  const [createForm] = Form.useForm()
  const [decisionForm] = Form.useForm()
  const [measureForm] = Form.useForm()
  const [transitionForm] = Form.useForm()

  async function refreshList() {
    setLoading(true)
    try {
      const data = await listRiskEvents(statusFilter)
      setEvents(data)
      if (!selectedId && data.length > 0) setSelectedId(data[0].id)
    } catch (e: any) {
      message.error(e?.message || '加载事件失败')
    } finally {
      setLoading(false)
    }
  }

  async function refreshDetail(id: string) {
    setDetailLoading(true)
    try {
      const d = await getRiskEventDetail(id)
      setDetail(d)
    } catch (e: any) {
      setDetail(null)
      message.error(e?.message || '加载详情失败')
    } finally {
      setDetailLoading(false)
    }
  }

  useEffect(() => {
    refreshList()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter])

  useEffect(() => {
    if (selectedId) refreshDetail(selectedId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId])

  const flow = useMemo(() => buildFlow(detail?.step), [detail?.step])

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '类型', dataIndex: 'event_type', key: 'event_type', width: 120, render: (v: string) => <Tag>{v}</Tag> },
    {
      title: '严重级别',
      dataIndex: 'severity',
      key: 'severity',
      width: 120,
      render: (v: string) => {
        const m: Record<string, string> = { low: 'green', medium: 'blue', high: 'orange', critical: 'red' }
        return <Tag color={m[v] || 'default'}>{v}</Tag>
      },
    },
    { title: '状态', dataIndex: 'status', key: 'status', width: 120, render: (v: string) => statusBadge(v) },
    { title: '流程', dataIndex: 'step', key: 'step', width: 90, render: (v: string) => stepTag(v) },
  ]

  const nextStepOptions = useMemo(() => {
    const s = detail?.step as StepKey | undefined
    if (!s) return []
    const order: StepKey[] = ['step1_detected', 'step2_assess_decide', 'step3_execute_measures', 'step4_follow_up']
    const idx = order.indexOf(s)
    return idx >= 0 && idx < order.length - 1 ? [order[idx + 1]] : []
  }, [detail?.step])

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>风控事件看板</h1>
        <Space>
          <Select
            placeholder="状态筛选"
            allowClear
            style={{ width: 160 }}
            value={statusFilter}
            onChange={(v) => setStatusFilter(v)}
            options={[
              { value: 'open', label: '开放' },
              { value: 'in_progress', label: '处理中' },
              { value: 'resolved', label: '已解决' },
              { value: 'closed', label: '已关闭' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={refreshList} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            新建事件
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={10}>
          <Card title="事件列表" bodyStyle={{ padding: 0 }}>
            <Table
              columns={columns as any}
              dataSource={events}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 8, showSizeChanger: false }}
              size="small"
              rowClassName={(r) => (r.id === selectedId ? 'ant-table-row-selected' : '')}
              onRow={(record) => ({
                onClick: () => setSelectedId(record.id),
              })}
            />
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card
            title="事件详情"
            loading={detailLoading}
            extra={
              detail ? (
                <Space>
                  <Button onClick={() => setDecisionOpen(true)}>新增决策</Button>
                  <Button onClick={() => setMeasureOpen(true)}>新增措施</Button>
                  <Button type="primary" icon={<ArrowRightOutlined />} onClick={() => setTransitionOpen(true)}>
                    推进流程
                  </Button>
                </Space>
              ) : null
            }
          >
            {!detail ? (
              <div style={{ color: '#999' }}>请选择左侧事件查看详情</div>
            ) : (
              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                <Descriptions bordered size="small" column={2}>
                  <Descriptions.Item label="标题" span={2}>
                    <Space>
                      <Text strong>{detail.title}</Text>
                      {statusBadge(detail.status)}
                      {stepTag(detail.step)}
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="类型">{detail.event_type}</Descriptions.Item>
                  <Descriptions.Item label="严重级别">{detail.severity}</Descriptions.Item>
                  <Descriptions.Item label="发现时间">{detail.detected_at || '-'}</Descriptions.Item>
                  <Descriptions.Item label="解决时间">{detail.resolved_at || '-'}</Descriptions.Item>
                  <Descriptions.Item label="描述" span={2}>
                    {detail.description || <Text type="secondary">无</Text>}
                  </Descriptions.Item>
                </Descriptions>

                <Card title="流程节点" size="small" styles={{ body: { padding: 0 } }}>
                  <div style={{ height: 170 }}>
                    <ReactFlow nodes={flow.nodes} edges={flow.edges} fitView>
                      <Background />
                      <Controls />
                    </ReactFlow>
                  </div>
                </Card>

                <Tabs
                  items={[
                    {
                      key: 'decisions',
                      label: `决策（${detail.decisions.length}）`,
                      children: (
                        <List
                          dataSource={detail.decisions}
                          locale={{ emptyText: '暂无决策记录' }}
                          renderItem={(d) => (
                            <List.Item>
                              <List.Item.Meta
                                title={
                                  <Space>
                                    <Tag color="blue">{d.decision}</Tag>
                                    <Text>{d.summary}</Text>
                                  </Space>
                                }
                                description={<Text type="secondary">{d.created_at}</Text>}
                              />
                            </List.Item>
                          )}
                        />
                      ),
                    },
                    {
                      key: 'measures',
                      label: `措施（${detail.measures.length}）`,
                      children: (
                        <List
                          dataSource={detail.measures}
                          locale={{ emptyText: '暂无措施记录' }}
                          renderItem={(m) => (
                            <List.Item>
                              <List.Item.Meta
                                title={
                                  <Space>
                                    {stepTag(m.step)}
                                    <Tag>{m.measure_type}</Tag>
                                    <Text>{m.description}</Text>
                                  </Space>
                                }
                                description={
                                  <Space>
                                    <Text type="secondary">owner: {m.owner || '-'}</Text>
                                    <Text type="secondary">status: {m.status}</Text>
                                    <Text type="secondary">{m.created_at}</Text>
                                  </Space>
                                }
                              />
                            </List.Item>
                          )}
                        />
                      ),
                    },
                  ]}
                />
              </Space>
            )}
          </Card>
        </Col>
      </Row>

      <Drawer
        title="新建风控事件"
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        width={520}
        destroyOnClose
        extra={
          <Space>
            <Button onClick={() => setCreateOpen(false)}>取消</Button>
            <Button
              type="primary"
              onClick={async () => {
                const v = await createForm.validateFields()
                try {
                  const e = await createRiskEvent(v)
                  message.success('创建成功')
                  setCreateOpen(false)
                  createForm.resetFields()
                  await refreshList()
                  setSelectedId(e.id)
                } catch (err: any) {
                  message.error(err?.message || '创建失败')
                }
              }}
            >
              创建
            </Button>
          </Space>
        }
      >
        <Form form={createForm} layout="vertical" initialValues={{ severity: 'medium', event_type: 'trading', source_role: 'trader' }}>
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="例如：单票仓位超限 / 异常成交 / 账户回撤超阈值" />
          </Form.Item>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="event_type" label="类型" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: 'trading', label: 'trading' },
                    { value: 'compliance', label: 'compliance' },
                    { value: 'market', label: 'market' },
                    { value: 'model', label: 'model' },
                    { value: 'other', label: 'other' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="severity" label="严重级别" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: 'low', label: 'low' },
                    { value: 'medium', label: 'medium' },
                    { value: 'high', label: 'high' },
                    { value: 'critical', label: 'critical' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="source_role" label="来源角色">
            <Select
              options={[
                { value: 'trader', label: 'trader' },
                { value: 'risk_officer', label: 'risk_officer' },
                { value: 'investment_manager', label: 'investment_manager' },
                { value: 'committee', label: 'committee' },
                { value: 'ops', label: 'ops' },
                { value: 'other', label: 'other' },
              ]}
            />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={5} placeholder="补充事件背景、触发条件、影响范围等" />
          </Form.Item>
        </Form>
      </Drawer>

      <Modal
        title="新增决策（Step2）"
        open={decisionOpen}
        onCancel={() => setDecisionOpen(false)}
        destroyOnClose
        okText="提交"
        onOk={async () => {
          if (!detail) return
          const v = await decisionForm.validateFields()
          try {
            await addRiskDecision(detail.id, { ...v, committee_members: [], attachments: [] })
            message.success('已记录决策')
            setDecisionOpen(false)
            decisionForm.resetFields()
            await refreshDetail(detail.id)
          } catch (err: any) {
            message.error(err?.message || '提交失败')
          }
        }}
      >
        <Form form={decisionForm} layout="vertical">
          <Form.Item name="decision" label="决策类型" rules={[{ required: true }]}>
            <Select
              options={[
                { value: 'continue', label: 'continue（继续）' },
                { value: 'reduce', label: 'reduce（减仓）' },
                { value: 'close', label: 'close（平仓/停止）' },
                { value: 'hedge', label: 'hedge（对冲）' },
                { value: 'other', label: 'other' },
              ]}
            />
          </Form.Item>
          <Form.Item name="summary" label="会议纪要/结论" rules={[{ required: true, message: '请输入纪要/结论' }]}>
            <Input.TextArea rows={4} placeholder="影响范围、风险程度、决策与依据" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="新增措施（Step3/Step4）"
        open={measureOpen}
        onCancel={() => setMeasureOpen(false)}
        destroyOnClose
        okText="提交"
        onOk={async () => {
          if (!detail) return
          const v = await measureForm.validateFields()
          try {
            await addRiskMeasure(detail.id, v)
            message.success('已新增措施')
            setMeasureOpen(false)
            measureForm.resetFields()
            await refreshDetail(detail.id)
          } catch (err: any) {
            message.error(err?.message || '提交失败')
          }
        }}
      >
        <Form form={measureForm} layout="vertical" initialValues={{ step: 'step3_execute_measures', status: 'open' }}>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="step" label="所属阶段" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: 'step3_execute_measures', label: 'Step3 执行措施' },
                    { value: 'step4_follow_up', label: 'Step4 优化复盘' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="measure_type" label="措施类型" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: 'position_limit', label: 'position_limit' },
                    { value: 'stop_loss', label: 'stop_loss' },
                    { value: 'process_fix', label: 'process_fix' },
                    { value: 'alerting', label: 'alerting' },
                    { value: 'other', label: 'other' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="措施描述" rules={[{ required: true }]}>
            <Input.TextArea rows={3} placeholder="例如：下调单票上限至 5%，新增回撤熔断规则..." />
          </Form.Item>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="owner" label="负责人">
                <Input placeholder="姓名/团队" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="状态" rules={[{ required: true }]}>
                <Select
                  options={[
                    { value: 'open', label: 'open' },
                    { value: 'in_progress', label: 'in_progress' },
                    { value: 'done', label: 'done' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="result" label="结果/备注">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="extra" label="扩展字段(JSON)" tooltip="可为空；不合法 JSON 会被当作空对象">
            <Input.TextArea
              rows={2}
              placeholder='例如：{"limit":0.05,"scope":"portfolio"}'
              onBlur={() => {
                const v = measureForm.getFieldValue('extra')
                if (typeof v === 'string' && v.trim()) {
                  try {
                    measureForm.setFieldValue('extra', JSON.parse(v))
                  } catch {
                    measureForm.setFieldValue('extra', {})
                  }
                }
              }}
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="推进流程（只允许按顺序 Step1→2→3→4）"
        open={transitionOpen}
        onCancel={() => setTransitionOpen(false)}
        destroyOnClose
        okText="推进"
        onOk={async () => {
          if (!detail) return
          const v = await transitionForm.validateFields()
          try {
            await transitionRiskEvent(detail.id, v)
            message.success('流程已推进')
            setTransitionOpen(false)
            transitionForm.resetFields()
            await refreshDetail(detail.id)
            await refreshList()
          } catch (err: any) {
            message.error(err?.response?.data?.detail || err?.message || '推进失败')
          }
        }}
      >
        <Form form={transitionForm} layout="vertical" initialValues={{ operator: 'system' }}>
          <Form.Item name="to_step" label="目标步骤" rules={[{ required: true }]}>
            <Select options={nextStepOptions.map((s) => ({ value: s, label: stepMeta[s].title }))} />
          </Form.Item>
          <Form.Item name="operator" label="操作人" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="reason" label="原因/说明" rules={[{ required: true }]}>
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Risk

