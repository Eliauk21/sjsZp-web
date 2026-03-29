import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  message,
  Modal,
  Upload,
  Typography,
  Popconfirm,
} from 'antd';
import {
  UploadOutlined,
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { shopApi } from '@/services/api';
import type { Shop } from '../../types';

const { Title } = Typography;

const NewShops: React.FC = () => {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadShops();
  }, []);

  const loadShops = async () => {
    setLoading(true);
    try {
      const res = await shopApi.getCurrentShops();
      setShops(res.data.data || []);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await shopApi.saveCurrentShops(shops);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleImport: UploadProps['onChange'] = async (info) => {
    if (info.file.status === 'done') {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          await shopApi.saveCurrentShops(data);
          setShops(data);
          message.success('导入成功');
        } catch (error) {
          message.error('导入失败');
        }
      };
      reader.readAsText(info.file.originFileObj as File);
    }
  };

  const handleDelete = (record: Shop) => {
    setShops(shops.filter(s => s.shopId !== record.shopId));
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
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Shop) => (
        <Popconfirm
          title="确认删除"
          onConfirm={() => handleDelete(record)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const uploadProps: UploadProps = {
    accept: '.json',
    onChange: handleImport,
    showUploadList: false,
    action: 'http://localhost:5174',
  };

  return (
    <div>
      <Title level={2}>➕ 新增入驻店铺</Title>
      <Typography.Text type="secondary">
        管理当前任务店铺配置 (zipdist/shopConfig.json)
      </Typography.Text>

      <Space style={{ marginBottom: 16, marginTop: 16 }}>
        <Upload {...uploadProps}>
          <Button icon={<UploadOutlined />}>JSON 导入</Button>
        </Upload>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
        >
          保存修改
        </Button>
        <Button
          icon={<PlusOutlined />}
          onClick={() => setShops([...shops, { shopId: '', shopName: '', templateId: null, orderId: null }])}
        >
          添加一行
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

export default NewShops;
