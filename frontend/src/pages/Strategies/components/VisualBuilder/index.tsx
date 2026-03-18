import React, { useCallback, useRef, useState, DragEvent } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Connection,
  Edge,
  Node
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button, Space, Typography, Card, Divider } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { nodeTypes } from './CustomNodes';

const { Title, Text } = Typography;

interface VisualBuilderProps {
  initialCanvasData?: any;
  onSave: (canvasData: any, generatedCode?: string) => void;
  isSaving?: boolean;
}

// 侧边栏可拖拽组件
const Sidebar = () => {
  const onDragStart = (event: DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/reactflow-label', label);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Card title="组件库" size="small" style={{ width: 250, height: '100%', borderRadius: 0, borderRight: '1px solid #f0f0f0', borderTop: 0, borderBottom: 0, borderLeft: 0 }}>
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>拖拽节点到画布</Text>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div 
          style={{ padding: '8px 12px', border: '1px solid #1890ff', borderRadius: 4, cursor: 'grab', background: '#e6f7ff' }} 
          onDragStart={(e) => onDragStart(e, 'data', '沪深300指数')} 
          draggable
        >
          数据源 (Data)
        </div>
        <div 
          style={{ padding: '8px 12px', border: '1px solid #52c41a', borderRadius: 4, cursor: 'grab', background: '#f6ffed' }} 
          onDragStart={(e) => onDragStart(e, 'indicator', '计算 MA20')} 
          draggable
        >
          技术指标 (Indicator)
        </div>
        <div 
          style={{ padding: '8px 12px', border: '1px solid #faad14', borderRadius: 4, cursor: 'grab', background: '#fffbe6' }} 
          onDragStart={(e) => onDragStart(e, 'signal', '价格 > MA20')} 
          draggable
        >
          交易信号 (Signal)
        </div>
        <div 
          style={{ padding: '8px 12px', border: '1px solid #f5222d', borderRadius: 4, cursor: 'grab', background: '#fff1f0' }} 
          onDragStart={(e) => onDragStart(e, 'action', '全仓买入')} 
          draggable
        >
          执行动作 (Action)
        </div>
      </div>
      <Divider />
      <Text type="secondary" style={{ fontSize: 12 }}>
        注意：构建需符合从 Data {'>'} Indicator {'>'} Signal {'>'} Action 的有向无环流程。
      </Text>
    </Card>
  );
};

let id = 0;
const getId = () => `node_v_${id++}`;

const VisualBuilderInner: React.FC<VisualBuilderProps> = ({ initialCanvasData, onSave, isSaving }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialCanvasData?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialCanvasData?.edges || []);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);

  const onConnect = useCallback((params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      const label = event.dataTransfer.getData('application/reactflow-label');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: getId(),
        type,
        position,
        data: { label: label },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );
  
  const handleSave = () => {
    if (reactFlowInstance) {
        const flow = reactFlowInstance.toObject();
        onSave(flow);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ padding: '12px 24px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={5} style={{ margin: 0 }}>可视化策略设计器</Title>
            <Space>
                <Button 
                    type="primary" 
                    icon={<SaveOutlined />} 
                    onClick={handleSave} 
                    loading={isSaving}
                >
                    保存并生成代码
                </Button>
            </Space>
        </div>
        <div style={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
            <Sidebar />
            <div className="reactflow-wrapper" ref={reactFlowWrapper} style={{ flexGrow: 1, height: '100%' }}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onInit={setReactFlowInstance}
                    onDrop={onDrop}
                    onDragOver={onDragOver}
                    nodeTypes={nodeTypes}
                    fitView
                    attributionPosition="bottom-right"
                >
                    <Controls />
                    <Background color="#aaa" gap={16} />
                </ReactFlow>
            </div>
        </div>
    </div>
  );
};

const VisualBuilder: React.FC<VisualBuilderProps> = (props) => (
  <ReactFlowProvider>
    <VisualBuilderInner {...props} />
  </ReactFlowProvider>
);

export default VisualBuilder;
