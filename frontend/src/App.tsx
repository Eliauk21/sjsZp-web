import React, { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  SettingOutlined,
  ShopOutlined,
  HistoryOutlined,
  FolderOutlined,
  PictureOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  FrownOutlined,
  SearchOutlined,  
  DeleteOutlined,
  CheckCircleOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import NewShops from './pages/NewShops';
import HistoryShops from './pages/HistoryShops';
import Modules from './pages/Modules';
import TaskImage from './pages/tasks/Image';
import TaskOrderReview from './pages/tasks/OrderReview';
import TaskCreateTemplate from './pages/tasks/CreateTemplate';
import TaskCreateV3 from './pages/tasks/CreateV3';
import TaskCheckModule from './pages/tasks/CheckModule';
import TaskCreateV4 from './pages/tasks/CreateV4';
import TaskDeleteModule from './pages/tasks/DeleteModule';
import TaskSubmitReview from './pages/tasks/SubmitReview';
import Settings from './pages/Settings';

const { Header, Content, Footer, Sider } = Layout;

type MenuItem = Required<MenuProps>['items'][number];

const menuItems: MenuItem[] = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '数据面板',
  },
  {
    key: 'data',
    icon: <FolderOutlined />,
    label: '数据维护',
    children: [
      { key: 'new-shops', icon: <ShopOutlined />, label: '新增入驻店铺' },
      { key: 'history-shops', icon: <HistoryOutlined />, label: '历史入驻店铺' },
      { key: 'modules', icon: <FolderOutlined />, label: '模块一览' },
    ],
  },
  {
    key: 'tasks',
    icon: <CloudUploadOutlined />,
    label: '任务操作',
    children: [
      { key: 'task-image', icon: <PictureOutlined />, label: '图片生成' },
      { key: 'task-order', icon: <FileTextOutlined />, label: '店铺订单预审' },
      { key: 'task-template', icon: <AppstoreOutlined />, label: '创建店铺模板' },
      { key: 'task-v3', icon: <FrownOutlined />, label: '创建 v3 版本模块' },
      { key: 'task-check', icon: <SearchOutlined />, label: '模块状态检查' },
      { key: 'task-v4', icon: <FrownOutlined />, label: '创建 v4 版本模块' },
      { key: 'task-delete', icon: <DeleteOutlined />, label: '删除指定模块' },
      { key: 'task-submit', icon: <CheckCircleOutlined />, label: '提交审核' },
    ],
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: '系统设置',
  },
];

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [selectedKey, setSelectedKey] = useState('dashboard');

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const renderPage = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'new-shops':
        return <NewShops />;
      case 'history-shops':
        return <HistoryShops />;
      case 'modules':
        return <Modules />;
      case 'task-image':
        return <TaskImage />;
      case 'task-order':
        return <TaskOrderReview />;
      case 'task-template':
        return <TaskCreateTemplate />;
      case 'task-v3':
        return <TaskCreateV3 />;
      case 'task-check':
        return <TaskCheckModule />;
      case 'task-v4':
        return <TaskCreateV4 />;
      case 'task-delete':
        return <TaskDeleteModule />;
      case 'task-submit':
        return <TaskSubmitReview />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)}>
        <div style={{
          height: 32,
          margin: 16,
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: 'bold',
        }}>
          {collapsed ? '🛒' : 'sjsZp 管理工具'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onSelect={({ key }) => setSelectedKey(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer }} />
        <Content style={{ margin: '16px' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {renderPage()}
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          sjsZp 管理工具 ©{new Date().getFullYear()} Created with React + Ant Design
        </Footer>
      </Layout>
    </Layout>
  );
};

export default App;
