import React from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  BulbOutlined,
  ExperimentOutlined,
  SwapOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  SafetyOutlined,
  AppstoreAddOutlined,
  StockOutlined,
} from '@ant-design/icons'

const { Sider } = Layout

const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/market',
    icon: <StockOutlined />,
    label: '大盘浏览',
  },
  {
    key: '/strategies',
    icon: <BulbOutlined />,
    label: '策略管理',
  },
  {
    key: '/components',
    icon: <AppstoreAddOutlined />,
    label: '组件库',
  },
  {
    key: '/backtest',
    icon: <ExperimentOutlined />,
    label: '回测系统',
  },
  {
    key: '/trading',
    icon: <SwapOutlined />,
    label: '实盘交易',
  },
  {
    key: '/risk',
    icon: <SafetyOutlined />,
    label: '风控看板',
  },
  {
    key: '/data',
    icon: <DatabaseOutlined />,
    label: '数据查询',
  },
  {
    key: '/reports',
    icon: <FileTextOutlined />,
    label: '报告中心',
  },
]

interface MainLayoutProps {
  children: React.ReactNode
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} style={{ background: '#fff' }}>
        <div style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <h2 style={{ margin: 0, color: '#52c41a' }}>浦渡量化交易系统</h2>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          style={{ height: '100%', borderRight: 0 }}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Layout.Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', height: '100%' }}>
            <span>欢迎使用浦渡量化交易系统</span>
          </div>
        </Layout.Header>
        {children}
      </Layout>
    </Layout>
  )
}

export default MainLayout
