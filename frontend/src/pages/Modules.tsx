import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  message,
  Typography,
  Image,
  Modal,
  Upload,
  Select,
} from 'antd';
import { SaveOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { moduleApi, shopApi } from '@/services/api';
import type { Module, Shop } from '../../types';

const { Title } = Typography;

const Modules: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedShopId, setSelectedShopId] = useState<string>('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadModules();
    loadShops();
  }, []);

  const loadModules = async () => {
    setLoading(true);
    try {
      const res = await moduleApi.getModules();
      setModules(res.data.data || []);
    } catch (error) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadShops = async () => {
    try {
      const res = await shopApi.getCurrentShops();
      const shopList = res.data.data || [];
      setShops(shopList);
      if (shopList.length > 0) {
        setSelectedShopId(shopList[0].shopId);
      }
    } catch (error) {
      console.error('加载店铺失败:', error);
    }
  };

  const handleSave = async () => {
    try {
      await moduleApi.saveModules(modules);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  const handleUpload = async (file: File) => {
    if (!selectedShopId) {
      message.error('请先选择店铺');
      return false;
    }

    setUploading(true);
    try {
      await moduleApi.uploadModule(file, selectedShopId);
      message.success(`上传成功到 zipdist/${selectedShopId}/${file.name}`);
    } catch (error) {
      message.error('上传失败');
    } finally {
      setUploading(false);
    }
    return false;
  };

  const columns = [
    {
      title: '模块名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '文件名',
      dataIndex: 'fileName',
      key: 'fileName',
    },
    {
      title: '会员卡模块',
      dataIndex: 'isMemberCard',
      key: 'isMemberCard',
      render: (val: boolean) => val ? '是' : '否',
    },
    {
      title: '模块图片',
      dataIndex: 'img',
      key: 'img',
      render: (img: string) => (
        <Image
          src={img}
          alt="模块预览"
          width={60}
          height={60}
          style={{ objectFit: 'cover' }}
        />
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>🧩 模块一览</Title>
      <Typography.Text type="secondary">
        管理模块配置 (moduleConfig.json)
      </Typography.Text>

      <Space style={{ marginBottom: 16, marginTop: 16 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
        >
          保存修改
        </Button>
        <Button
          icon={<PlusOutlined />}
          onClick={() => setModules([...modules, { name: '', fileName: '', isMemberCard: false, img: '' }])}
        >
          添加模块
        </Button>
        <Select
          value={selectedShopId}
          onChange={setSelectedShopId}
          options={shops.map(s => ({ label: s.shopName, value: s.shopId }))}
          style={{ width: 200 }}
          placeholder="选择店铺"
        />
        <Upload
          accept=".zip"
          beforeUpload={handleUpload}
          showUploadList={false}
        >
          <Button icon={<UploadOutlined />} loading={uploading}>
            上传模块 zip
          </Button>
        </Upload>
      </Space>

      <Table
        columns={columns}
        dataSource={modules}
        rowKey="name"
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />

      <Title level={4} style={{ marginTop: 24 }}>模块图片预览</Title>
      <Space wrap>
        {modules.map((module) => (
          <div key={module.name} style={{ textAlign: 'center' }}>
            <Image
              src={module.img}
              alt={module.name}
              width={120}
              height={80}
              style={{ objectFit: 'cover' }}
            />
            <div style={{ fontSize: 12, marginTop: 4 }}>{module.name}</div>
          </div>
        ))}
      </Space>
    </div>
  );
};

export default Modules;
