import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Modal, Form, Input, Select, Tabs, message, Drawer, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, SaveOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { getStrategies, createStrategy, updateStrategy, deleteStrategy } from '../../services/strategy';
import type { Strategy, StrategyCreatePayload } from '../../types/strategy';
import CodeEditor from './CodeEditor';
import VisualBuilder from './components/VisualBuilder';

const { Option } = Select;
const { TextArea } = Input;

const INITIAL_CODE_TEMPLATE = `def init(context):
    """
    策略初始化函数
    :param context: 策略上下文环境
    """
    # 设置基准收益
    context.set_benchmark('000300.XSHG')
    # 设置股票池
    context.universe = ['000001.XSHE', '600000.XSHG']

def handle_bar(context, bar_dict):
    """
    K线处理函数
    :param context: 策略上下文环境
    :param bar_dict: 行情数据字典
    """
    for stock in context.universe:
        history = context.history(stock, 'close', 20, '1d')
        # ... 实现交易逻辑
`;

const Strategies: React.FC = () => {
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  
  const [activeTab, setActiveTab] = useState('code');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isDrawerVisible, setIsDrawerVisible] = useState(false);
  
  const [isVisualDrawerVisible, setIsVisualDrawerVisible] = useState(false);
  
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [currentCode, setCurrentCode] = useState('');
  const [currentCanvasData, setCurrentCanvasData] = useState<any>(null);

  // Queries
  const { data: strategiesData, isLoading } = useQuery({
    queryKey: ['strategies', activeTab],
    queryFn: () => getStrategies({ limit: 100, category: undefined }),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: createStrategy,
    onSuccess: () => {
      message.success('策略创建成功');
      setIsModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
    onError: (err: any) => message.error(err.response?.data?.detail || '创建策略失败')
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string, data: any }) => updateStrategy(id, data),
    onSuccess: () => {
      message.success('策略更新成功');
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
    onError: (err: any) => message.error(err.response?.data?.detail || '更新失败')
  });

  const deleteMutation = useMutation({
    mutationFn: deleteStrategy,
    onSuccess: () => {
      message.success('策略删除成功');
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
    onError: (err: any) => message.error(err.response?.data?.detail || '删除失败')
  });

  // Handlers
  const handleCreate = (values: any) => {
    const payload: StrategyCreatePayload = {
      name: values.name,
      type: values.type,
      description: values.description,
      category: values.category,
      code: values.type === 'code' ? INITIAL_CODE_TEMPLATE : '',
    };
    createMutation.mutate(payload);
  };

  const handleEditCode = (record: Strategy) => {
    setEditingStrategy(record);
    setCurrentCode(record.code || '');
    setIsDrawerVisible(true);
  };

  const handleEditVisual = (record: Strategy) => {
    setEditingStrategy(record);
    setCurrentCanvasData(record.canvas_data || { nodes: [], edges: [] });
    setIsVisualDrawerVisible(true);
  };

  const handleSaveCode = () => {
    if (!editingStrategy) return;
    updateMutation.mutate({
      id: editingStrategy.id,
      data: { code: currentCode }
    });
  };

  const handleSaveVisual = (canvasData: any) => {
    if (!editingStrategy) return;
    updateMutation.mutate({
      id: editingStrategy.id,
      data: { canvas_data: canvasData }
    });
  };

  const filteredStrategies = strategiesData?.items?.filter(
    (item) => (activeTab === 'code' && !item.is_visual) || (activeTab === 'visual' && item.is_visual)
  ) || [];

  const columns = [
    { title: '策略名称', dataIndex: 'name', key: 'name' },
    { title: '类别', dataIndex: 'category', key: 'category' },
    { title: '类型', dataIndex: 'is_visual', key: 'is_visual',
      render: (is_visual: boolean) => (
        <Tag color={is_visual ? 'green' : 'blue'}>
          {is_visual ? '可视化' : '代码编辑'}
        </Tag>
      )
    },
    { title: '状态', dataIndex: 'status', key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          active: 'green',
          draft: 'orange',
          archived: 'default'
        };
        const statusMap: Record<string, string> = {
          active: '运行中',
          draft: '草稿',
          archived: '已归档'
        };
        return <Tag color={colorMap[status] || 'default'}>{statusMap[status] || status}</Tag>;
      }
    },
    { title: '操作', key: 'action',
      render: (_: any, record: Strategy) => (
        <Space>
          <Button type="link" icon={<PlayCircleOutlined />}>运行配置</Button>
          {!record.is_visual ? (
             <Button type="link" icon={<EditOutlined />} onClick={() => handleEditCode(record)}>代码编辑</Button>
          ) : (
             <Button type="link" icon={<EditOutlined />} onClick={() => handleEditVisual(record)}>画布排版</Button>
          )}
          <Popconfirm
            title="确认删除该策略？"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      )
    },
  ];

  const tabItems = [
    { key: 'code', label: '代码编辑模式' },
    { key: 'visual', label: '可视化构建模式' },
  ];

  return (
    <div>
      <h1>策略管理</h1>
      
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
            新建策略
          </Button>
        </div>

        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />

        <Table 
          columns={columns} 
          dataSource={filteredStrategies} 
          rowKey="id" 
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="新建策略"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item label="策略名称" name="name" rules={[{ required: true }]}>
            <Input placeholder="请输入策略名称" />
          </Form.Item>
          <Form.Item label="分类标签" name="category">
            <Input placeholder="如：多因子、趋势追踪" />
          </Form.Item>
          <Form.Item label="策略类型" name="type" initialValue="code" rules={[{ required: true }]}>
            <Select>
              <Option value="code">代码编辑模式</Option>
              <Option value="visual">可视化构建模式</Option>
            </Select>
          </Form.Item>
          <Form.Item label="策略描述" name="description">
            <TextArea rows={4} placeholder="请输入简要描述" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={createMutation.isPending}>确认创建</Button>
          </Form.Item>
        </Form>
      </Modal>

      <Drawer
        title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>编写策略代码 - {editingStrategy?.name}</span>
                <Button 
                  type="primary" 
                  icon={<SaveOutlined />} 
                  onClick={handleSaveCode}
                  loading={updateMutation.isPending}
                >
                  保存代码
                </Button>
            </div>
        }
        placement="right"
        width="80vw"
        onClose={() => setIsDrawerVisible(false)}
        open={isDrawerVisible}
        destroyOnClose
        extra={null}
      >
        <div style={{ height: 'calc(100vh - 120px)' }}>
           <CodeEditor 
              value={currentCode} 
              onChange={(val) => setCurrentCode(val || '')} 
              height="100%"
           />
        </div>
      </Drawer>

      <Drawer
        title={`可视化构建 - ${editingStrategy?.name}`}
        placement="top"
        height="100vh"
        onClose={() => setIsVisualDrawerVisible(false)}
        open={isVisualDrawerVisible}
        destroyOnClose
        closable={true}
        bodyStyle={{ padding: 0 }}
      >
        <VisualBuilder 
           initialCanvasData={currentCanvasData}
           onSave={handleSaveVisual}
           isSaving={updateMutation.isPending}
        />
      </Drawer>
    </div>
  );
};

export default Strategies;
