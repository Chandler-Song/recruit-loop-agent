import React from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  AppstoreOutlined,
  TeamOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import DashboardPage from './pages/Dashboard/DashboardPage';
import PositionsPage from './pages/Positions/PositionsPage';
import CandidatesPage from './pages/Candidates/CandidatesPage';
import SchedulerPage from './pages/Scheduler/SchedulerPage';
import LogsPage from './pages/Logs/LogsPage';
import SettingsPage from './pages/Settings/SettingsPage';
import PositionDetailPage from './pages/PositionDetail/PositionDetailPage';

const { Header, Sider, Content } = Layout;

const App = () => {
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: '/positions',
      icon: <AppstoreOutlined />,
      label: <Link to="/positions">Positions</Link>,
    },
    {
      key: '/candidates',
      icon: <TeamOutlined />,
      label: <Link to="/candidates">Candidates</Link>,
    },
    {
      key: '/scheduler',
      icon: <CalendarOutlined />,
      label: <Link to="/scheduler">Scheduler</Link>,
    },
    {
      key: '/logs',
      icon: <FileTextOutlined />,
      label: <Link to="/logs">Logs</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">Settings</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={256} style={{ background: '#fff' }}>
        <div style={{ height: 32, margin: 16, textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
          Recruiting Loop Agent
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          style={{ height: '100%', borderRight: 0 }}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: 0,
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            paddingRight: 24,
          }}
        >
          <span>Recruiter</span>
        </Header>
        <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
          <div style={{ padding: 24, background: '#fff', textAlign: 'center' }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/positions" element={<PositionsPage />} />
              <Route path="/positions/:id" element={<PositionDetailPage />} />
              <Route path="/candidates" element={<CandidatesPage />} />
              <Route path="/scheduler" element={<SchedulerPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;