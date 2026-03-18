import React, { useState } from 'react';
import { Card, Table, Button, Tabs, Space, Popconfirm, Tag, message, Drawer, Form, Input } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SaveOutlined } from '@ant-design/icons';
import { useQuery, useQueryClient } from '@tanstack/react-query';

import { 
    getIndicators, createIndicator, updateIndicator, deleteIndicator,
    getSignals, createSignal, updateSignal, deleteSignal,
    getPositions, createPosition, updatePosition, deletePosition,
    getRiskRules, createRiskRule, updateRiskRule, deleteRiskRule
} from '../../services/custom';
import CodeEditor from '../Strategies/CodeEditor';

const { TextArea } = Input;

const INITIAL_FORMULA = `def calculate(data, params):
    # 此处编写自定义指标计算逻辑
    return []
`;

const INITIAL_SIGNAL = `{
    "condition": "price > ma20"
}`;

const ComponentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  
  const [activeTab, setActiveTab] = useState('indicator');
  const [isDrawerVisible, setIsDrawerVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [currentCode, setCurrentCode] = useState('');

  // 统一的获取抽象（按当前 Tab）
  const useActiveQuery = () => {
    switch (activeTab) {
        case 'indicator': return useQuery({ queryKey: ['custom-indicators'], queryFn: () => getIndicators() });
        case 'signal': return useQuery({ queryKey: ['custom-signals'], queryFn: () => getSignals() });
        case 'position': return useQuery({ queryKey: ['custom-positions'], queryFn: () => getPositions() });
        case 'risk': return useQuery({ queryKey: ['custom-risks'], queryFn: () => getRiskRules() });
        default: return useQuery({ queryKey: ['custom-indicators'], queryFn: () => getIndicators() });
    }
  };

  const { data: listData, isLoading } = useActiveQuery();

  // 删除操作映射表
  const handleDelete = async (id: string) => {
      try {
          if (activeTab === 'indicator') await deleteIndicator(id);
          else if (activeTab === 'signal') await deleteSignal(id);
          else if (activeTab === 'position') await deletePosition(id);
          else if (activeTab === 'risk') await deleteRiskRule(id);
          message.success('删除成功');
          queryClient.invalidateQueries({ queryKey: [`custom-${activeTab}s`] });
      } catch (e: any) {
          message.error(e.response?.data?.detail || '删除失败');
      }
  };

  const openEditorForCreate = () => {
      setEditingItem(null);
      form.resetFields();
      if (activeTab === 'indicator' || activeTab === 'position') {
          setCurrentCode(INITIAL_FORMULA);
      } else {
          setCurrentCode(INITIAL_SIGNAL);
      }
      setIsDrawerVisible(true);
  };

  const openEditorForEdit = (record: any) => {
      setEditingItem(record);
      form.setFieldsValue(record);
      
      let codeVal = '';
      if (activeTab === 'indicator') codeVal = record.formula;
      else if (activeTab === 'signal') codeVal = JSON.stringify(record.conditions, null, 2);
      else if (activeTab === 'position') codeVal = record.algorithm;
      else if (activeTab === 'risk') codeVal = JSON.stringify(record.rule_config, null, 2);
      
      setCurrentCode(codeVal);
      setIsDrawerVisible(true);
  };

  const handleSave = async () => {
      try {
          const values = await form.validateFields();
          
          let payload: any = { ...values };
          
          // 装配代码字段
          if (activeTab === 'indicator') {
              payload.formula = currentCode;
          } else if (activeTab === 'signal') {
              payload.conditions = JSON.parse(currentCode || '{}');
          } else if (activeTab === 'position') {
              payload.algorithm = currentCode;
          } else if (activeTab === 'risk') {
              payload.rule_config = JSON.parse(currentCode || '{}');
          }

          if (editingItem) {
              // Update
              if (activeTab === 'indicator') await updateIndicator(editingItem.id, payload);
              else if (activeTab === 'signal') await updateSignal(editingItem.id, payload);
              else if (activeTab === 'position') await updatePosition(editingItem.id, payload);
              else if (activeTab === 'risk') await updateRiskRule(editingItem.id, payload);
              message.success('更新成功');
          } else {
              // Create
              if (activeTab === 'indicator') await createIndicator(payload);
              else if (activeTab === 'signal') await createSignal(payload);
              else if (activeTab === 'position') await createPosition(payload);
              else if (activeTab === 'risk') await createRiskRule(payload);
              message.success('创建成功');
          }
          
          setIsDrawerVisible(false);
          queryClient.invalidateQueries({ queryKey: [`custom-${activeTab}s`] });
      } catch (e: any) {
          if (e.name === 'SyntaxError') {
              message.error('JSON 格式错误，请检查代码结构');
          } else {
              message.error(e.response?.data?.detail || '保存遇到异常');
          }
      }
  };

  const columns = [
    { title: '组件名称', dataIndex: 'name', key: 'name' },
    { title: '描述补充', dataIndex: 'description', key: 'description' },
    { title: '状态', dataIndex: 'is_public', key: 'is_public',
      render: (isPublic: boolean) => (
        <Tag color={isPublic ? 'green' : 'default'}>{isPublic ? '公有' : '私有'}</Tag>
      )
    },
    { title: '操作', key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => openEditorForEdit(record)}>编辑设定</Button>
          <Popconfirm
            title="确认删除该组件？已有的策略关联可能受到影响。"
            onConfirm={() => handleDelete(record.id)}
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
    { key: 'indicator', label: '自定义指标 (Indicators)' },
    { key: 'signal', label: '自定义信号 (Signals)' },
    { key: 'position', label: '仓位算法 (Positions)' },
    { key: 'risk', label: '风控组件 (Risk Rules)' },
  ];

  const getEditorLanguage = () => {
      return (activeTab === 'indicator' || activeTab === 'position') ? 'python' : 'json';
  };

  return (
    <div>
      <h1>组件库中心</h1>
      
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={openEditorForCreate}>
            新建构件
          </Button>
        </div>

        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />

        <Table 
          columns={columns} 
          dataSource={listData?.items || []} 
          rowKey="id" 
          loading={isLoading}
          pagination={{ pageSize: 15 }}
        />
      </Card>

      <Drawer
        title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{editingItem ? '编辑' : '新建'}组件 - {tabItems.find(t => t.key === activeTab)?.label}</span>
                <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
                  保存组件配置
                </Button>
            </div>
        }
        placement="right"
        width="60vw"
        onClose={() => setIsDrawerVisible(false)}
        open={isDrawerVisible}
        destroyOnClose
        extra={null}
      >
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ padding: '0 0 24px 0' }}>
               <Form layout="horizontal" form={form} labelCol={{ span: 4 }} wrapperCol={{ span: 18 }}>
                  <Form.Item label="构件名" name="name" rules={[{ required: true }]}>
                    <Input placeholder="输入此组件调用的标识名词" />
                  </Form.Item>
                  <Form.Item label="文字说明" name="description">
                    <TextArea rows={2} placeholder="组件逻辑介绍" />
                  </Form.Item>
               </Form>
            </div>
            <div style={{ flexGrow: 1, border: '1px solid #d9d9d9', borderRadius: 4, overflow: 'hidden' }}>
               <CodeEditor 
                  value={currentCode} 
                  onChange={(val) => setCurrentCode(val || '')} 
                  height="100%"
                  language={getEditorLanguage()}
               />
            </div>
        </div>
      </Drawer>
    </div>
  );
};

export default ComponentsPage;
