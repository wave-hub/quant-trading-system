import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import MainLayout from './components/Layout/MainLayout'
import Dashboard from './pages/Dashboard'
import Strategies from './pages/Strategies'
import Trading from './pages/Trading'
import Data from './pages/Data'
import Reports from './pages/Reports'
import Risk from './pages/Risk'
import ComponentsPage from './pages/Components'
import Backtest from './pages/Backtest'
import Market from './pages/Market'

const { Content } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <MainLayout>
        <Content style={{ padding: '24px', background: '#fff' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/market" element={<Market />} />
            <Route path="/data" element={<Data />} />
            <Route path="/strategies" element={<Strategies />} />
            <Route path="/components" element={<ComponentsPage />} />
            <Route path="/backtest" element={<Backtest />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/risk" element={<Risk />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Content>
      </MainLayout>
    </Layout>
  )
}

export default App
