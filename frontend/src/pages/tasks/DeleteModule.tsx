import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Typography, Modal, Select } from 'antd';
import { DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi, moduleApi } from '@/services/api';
import type { Module } from '../../types';

const { Title } = Typography;

const TaskDeleteModule: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    try {
      const res = await moduleApi.getModules();
      setModules(res.data.data || []);
    } catch (error) {
      message.error('加载模块失败');
    }
  };

  const handleExecute = async () => {
    Modal.confirm({
      title: '确认删除',
      content: `将删除所有店铺中选中的 ${selectedModules.length} 个模块，确认继续？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        setRunning(true);
        try {
          await taskApi.execute('delete_module', { modules: selectedModules });
          message.success('模块删除完成');
        } catch (error) {
          message.error('删除失败');
        } finally {
          setRunning(false);
        }
      },
    });
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <DeleteOutlined style={{ fontSize: 24 }} />
        <Title level={2} style={{ margin: 0 }}>🗑️ 删除指定模块</Title>
      </Space>

      <Typography.Text type="secondary">
        多选模块批量删除
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
        <Select
          mode="multiple"
          value={selectedModules}
          onChange={setSelectedModules}
          options={modules.map(m => ({ label: m.name, value: m.name }))}
          style={{ width: 300 }}
          placeholder="选择要删除的模块"
        />
        <Button
          type="primary"
          danger
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={running}
          disabled={!selectedModules.length}
        >
          开始删除
        </Button>
      </Space>
    </div>
  );
};

export default TaskDeleteModule;
