import React, { useState } from 'react';
import {
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Space,
  message,
  Image,
  Radio,
  Divider,
  ColorPicker,
} from 'antd';
import { PictureOutlined } from '@ant-design/icons';
import { taskApi, shopApi } from '@/services/api';

const { TextArea } = Input;

const TaskImage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'single' | 'batch'>('batch');
  const [shops, setShops] = useState<any[]>([]);

  React.useEffect(() => {
    loadShops();
  }, []);

  const loadShops = async () => {
    try {
      const res = await shopApi.getCurrentShops();
      setShops(res.data.data || []);
    } catch (error) {
      console.error('加载店铺失败:', error);
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const params = {
        mode,
        ...values,
        bg_color: values.bg_color?.toHexString?.() || '#ffffff',
        text_color: values.text_color?.toHexString?.() || '#000000',
        border_color: values.border_color?.toHexString?.() || '#000000',
      };
      const res = await taskApi.execute('generate_image', params);
      message.success(`生成完成！共 ${values.shops?.length || 1} 张图片`);
    } catch (error) {
      message.error('生成失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <PictureOutlined style={{ fontSize: 24 }} />
        <h2 style={{ margin: 0 }}>🖼️ 图片生成</h2>
      </Space>

      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item label="生成模式" required>
          <Radio.Group value={mode} onChange={(e) => setMode(e.target.value)}>
            <Radio value="batch">批量生成</Radio>
            <Radio value="single">单张生成</Radio>
          </Radio.Group>
        </Form.Item>

        {mode === 'batch' ? (
          <Form.Item
            name="shops"
            label="选择店铺"
            rules={[{ required: true, message: '请选择店铺' }]}
          >
            <Select
              mode="multiple"
              options={shops.map(s => ({ label: s.shopName, value: s.shopName }))}
              placeholder="请选择店铺"
            />
          </Form.Item>
        ) : (
          <Form.Item
            name="text"
            label="店铺名称"
            rules={[{ required: true, message: '请输入店铺名称' }]}
          >
            <Input placeholder="请输入店铺名称" />
          </Form.Item>
        )}

        {mode === 'single' && (
          <>
            <Divider>图片参数</Divider>
            <Form.Item name="bg_color" label="背景颜色">
              <ColorPicker defaultValue="#ffffff" />
            </Form.Item>
            <Form.Item name="text_color" label="文字颜色">
              <ColorPicker defaultValue="#000000" />
            </Form.Item>
            <Form.Item name="border_color" label="围边颜色">
              <ColorPicker defaultValue="#000000" />
            </Form.Item>
            <Form.Item name="border_width" label="围边宽度 (像素)">
              <InputNumber min={0} max={50} defaultValue={20} />
            </Form.Item>
            <Form.Item name="font_size" label="字体大小 (像素)">
              <InputNumber min={20} max={100} defaultValue={40} />
            </Form.Item>
          </>
        )}

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            开始生成
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default TaskImage;
