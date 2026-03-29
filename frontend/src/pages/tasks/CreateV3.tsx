import React, { useState } from 'react';
import { Table, Button, Space, message, Typography, Modal, Select } from 'antd';
import { FrownOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi, shopApi, moduleApi } from '@/services/api';
import type { Shop, Module } from '../../types';

const { Title } = Typography;

const TaskCreateV3: React.FC = () => {
  const [shops, setShops] = useState<Shop[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [running, setRunning] = useState(false);

  React.useEffect(() => {
    loadShops();
    loadModules();
  }, []);

  const loadShops = async () => {
    try {
      const res = await shopApi.getCurrentShops();
      setShops(res.data.data || []);
    } catch (error) {
      message.error('加载店铺失败');
    }
  };

  const loadModules = async () => {
    try {
      const res = await moduleApi.getModules();
      const modList = res.data.data || [];
      setModules(modList);
      setSelectedModules(modList.map((m: Module) => m.name));
    } catch (error) {
      message.error('加载模块失败');
    }
  };

  const handleExecute = async () => {
    Modal.confirm({
      title: '确认创建模块',
      content: `将为 ${shops.length} 家店铺创建 ${selectedModules.length} 个 v3 版本模块，确认继续？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        setRunning(true);
        try {
          await taskApi.execute('new_module', { shops, modules: selectedModules });
          message.success('v3 模块创建完成');
        } catch (error) {
          message.error('创建失败');
        } finally {
          setRunning(false);
        }
      },
    });
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {/*<FrownOutlined style={{ fontSize: 24 }} />*/}
        <Title level={2} style={{ margin: 0 }}>📦 创建 v3 版本模块</Title>
      </Space>

      <Typography.Text type="secondary">
        为新增入驻店铺创建 v3 版本模块
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
        <Select
          mode="multiple"
          value={selectedModules}
          onChange={setSelectedModules}
          options={modules.map(m => ({ label: m.name, value: m.name }))}
          style={{ width: 300 }}
          placeholder="选择要创建的模块"
        />
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={running}
        >
          开始创建
        </Button>
      </Space>

      <Table
        columns={[
          { title: '店铺 ID', dataIndex: 'shopId', key: 'shopId' },
          { title: '店铺名称', dataIndex: 'shopName', key: 'shopName' },
        ]}
        dataSource={shops}
        rowKey="shopId"
        pagination={{ pageSize: 10 }}
        size="small"
        scroll={{ x: 400 }}
      />
    </div>
  );
};

export default TaskCreateV3;
