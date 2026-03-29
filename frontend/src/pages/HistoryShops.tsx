import React, { useEffect, useState } from 'react';
import { Table, Button, Space, message, Typography } from 'antd';
import { SaveOutlined, SyncOutlined } from '@ant-design/icons';
import { shopApi } from '@/services/api';
import type { Shop } from '../../types';

const { Title } = Typography;

const HistoryShops: React.FC = () => {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadShops();
  }, []);

  const loadShops = async () => {
    setLoading(true);
    try {
      const res = await shopApi.getHistoryShops();
      setShops(res.data.data || []);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      const res = await shopApi.syncShops();
      message.success(res.data.message);
      loadShops();
    } catch (error) {
      message.error('同步失败');
    }
  };

  const handleSave = async () => {
    try {
      await shopApi.saveHistoryShops(shops);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
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
    {
      title: '订单 ID',
      dataIndex: 'orderId',
      key: 'orderId',
    },
  ];

  return (
    <div>
      <Title level={2}>📜 历史入驻店铺</Title>
      <Typography.Text type="secondary">
        管理历史店铺配置 (shopAllConfig.json)
      </Typography.Text>

      <Space style={{ marginBottom: 16, marginTop: 16 }}>
        <Button
          icon={<SyncOutlined />}
          onClick={handleSync}
        >
          同步新增店铺到历史
        </Button>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
        >
          保存修改
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={shops}
        rowKey="shopId"
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  );
};

export default HistoryShops;
