import React, { useState } from 'react';
import { Table, Button, Space, message, Typography, Modal } from 'antd';
import { AppstoreOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi, shopApi } from '@/services/api';
import type { Shop } from '../../types';

const { Title, Text } = Typography;

const TaskCreateTemplate: React.FC = () => {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  React.useEffect(() => {
    loadShops();
  }, []);

  const loadShops = async () => {
    try {
      const res = await shopApi.getCurrentShops();
      setShops(res.data.data || []);
    } catch (error) {
      message.error('加载店铺失败');
    }
  };

  const handleExecute = async () => {
    Modal.confirm({
      title: '确认创建模板',
      content: `将为 ${shops.length} 家店铺创建定制模板，确认继续？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        setRunning(true);
        try {
          await taskApi.execute('create_module', { shops });
          message.success('模板创建完成');
        } catch (error) {
          message.error('创建失败');
        } finally {
          setRunning(false);
        }
      },
    });
  };

  const columns = [
    {
      title: '店铺 ID',
      dataIndex: 'shopId',
      key: 'shopId',
    },
    {
      title: '店铺名称',
      dataIndex: 'shopName',
      key: 'shopName',
    },
    {
      title: '模板 ID',
      dataIndex: 'templateId',
      key: 'templateId',
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {/*<FrownOutlined style={{ fontSize: 24 }} />*/}
        <Title level={2} style={{ margin: 0 }}>🏪 创建店铺模板</Title>
      </Space>

      <Typography.Text type="secondary">
        为新增入驻店铺创建定制模板，共 {shops.length} 家
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
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
        columns={columns}
        dataSource={shops}
        rowKey="shopId"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  );
};

export default TaskCreateTemplate;
