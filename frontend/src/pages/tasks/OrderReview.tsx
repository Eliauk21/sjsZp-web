import React, { useState } from 'react';
import { Table, Button, Space, message, Typography, Modal, Tag } from 'antd';
import { FileTextOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi, shopApi } from '@/services/api';
import type { Shop } from '../../types';

const { Title, Text } = Typography;

const TaskOrderReview: React.FC = () => {
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
      title: '确认开始审核',
      content: `当前操作对象为新增入驻店铺，共 ${shops.length} 家，确认开始审核？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        setRunning(true);
        try {
          const res = await taskApi.execute('check_orderId', { shops });
          message.success('审核完成');
          loadShops();
        } catch (error) {
          message.error('审核失败');
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
      title: '订单 ID',
      dataIndex: 'orderId',
      key: 'orderId',
      render: (val: string | null) => val ? <Tag color="success">{val}</Tag> : <Tag>未获取</Tag>,
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <FileTextOutlined style={{ fontSize: 24 }} />
        <Title level={2} style={{ margin: 0 }}>📋 店铺订单预审</Title>
      </Space>

      <Typography.Text type="secondary">
        当前操作对象为新增入驻店铺，共 {shops.length} 家
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={running}
        >
          开始审核
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

export default TaskOrderReview;
