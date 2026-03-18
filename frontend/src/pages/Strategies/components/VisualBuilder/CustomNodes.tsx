import { Handle, Position } from 'reactflow';
import { Card, Typography } from 'antd';
import { DatabaseOutlined, LineChartOutlined, NodeIndexOutlined, DollarCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const DataNode = ({ data }: { data: any }) => (
  <Card size="small" style={{ width: 180, borderColor: '#1890ff', borderWidth: 2 }} title={
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <DatabaseOutlined style={{ color: '#1890ff' }} />
      <Text strong>数据节点</Text>
    </div>
  }>
    <Text type="secondary">{data.label || '选择交易标的'}</Text>
    <Handle type="source" position={Position.Right} id="out" style={{ background: '#1890ff' }} />
  </Card>
);

export const IndicatorNode = ({ data }: { data: any }) => (
  <Card size="small" style={{ width: 180, borderColor: '#52c41a', borderWidth: 2 }} title={
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <LineChartOutlined style={{ color: '#52c41a' }} />
      <Text strong>指标节点</Text>
    </div>
  }>
    <Handle type="target" position={Position.Left} id="in" style={{ background: '#52c41a' }} />
    <Text type="secondary">{data.label || '计算技术指标'}</Text>
    <Handle type="source" position={Position.Right} id="out" style={{ background: '#52c41a' }} />
  </Card>
);

export const SignalNode = ({ data }: { data: any }) => (
  <Card size="small" style={{ width: 180, borderColor: '#faad14', borderWidth: 2 }} title={
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <NodeIndexOutlined style={{ color: '#faad14' }} />
      <Text strong>信号节点</Text>
    </div>
  }>
    <Handle type="target" position={Position.Left} id="in" style={{ background: '#faad14' }} />
    <Text type="secondary">{data.label || '逻辑比较与触发'}</Text>
    <Handle type="source" position={Position.Right} id="out" style={{ background: '#faad14' }} />
  </Card>
);

export const ActionNode = ({ data }: { data: any }) => (
  <Card size="small" style={{ width: 180, borderColor: '#f5222d', borderWidth: 2 }} title={
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <DollarCircleOutlined style={{ color: '#f5222d' }} />
      <Text strong>交易节点</Text>
    </div>
  }>
    <Handle type="target" position={Position.Left} id="in" style={{ background: '#f5222d' }} />
    <Text type="secondary">{data.label || '执行买入/卖出'}</Text>
  </Card>
);

export const nodeTypes = {
  data: DataNode,
  indicator: IndicatorNode,
  signal: SignalNode,
  action: ActionNode,
};
