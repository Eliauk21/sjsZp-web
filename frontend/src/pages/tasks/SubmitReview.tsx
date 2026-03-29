import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Typography, Modal } from 'antd';
import { CheckCircleOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi, shopApi } from '@/services/api';
import type { Shop } from '../../types';

const { Title } = Typography;

const TaskSubmitReview: React.FC = () => {
  const [shops, setShops] = useState<Shop[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadShops();
  }, []);

  const loadShops = async () => {
    try {
      const res = await shopApi.getHistoryShops();
      setShops(res.data.data || []);
    } catch (error) {
      message.error('加载店铺失败');
    }
  };

  const handleExecute = async () => {
    Modal.confirm({
      title: '确认提审',
      content: `当前操作对象为历史入驻店铺，共 ${shops.length} 家，确认开始提审？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        setRunning(true);
        try {
          await taskApi.execute('review_module', { shops });
          message.success('审核提交完成');
        } catch (error) {
          message.error('提交失败');
        } finally {
          setRunning(false);
        }
      },
    });
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <CheckCircleOutlined style={{ fontSize: 24 }} />
        <Title level={2} style={{ margin: 0 }}>✅ 提交审核</Title>
      </Space>

      <Typography.Text type="secondary">
        一键提审历史入驻店铺，共 {shops.length} 家
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={running}
        >
          开始提审
        </Button>
      </Space>

      <Table
        columns={[
          { title: '店铺 ID', dataIndex: 'shopId', key: 'shopId' },
          { title: '店铺名称', dataIndex: 'shopName', key: 'shopName' },
          { title: '模板 ID', dataIndex: 'templateId', key: 'templateId' },
        ]}
        dataSource={shops}
        rowKey="shopId"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 600 }}
        size="small"
      />
    </div>
  );
};

export default TaskSubmitReview;
