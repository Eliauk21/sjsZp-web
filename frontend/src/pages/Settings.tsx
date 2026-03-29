import React, { useEffect, useState } from 'react';
import { Form, Input, Button, Space, message, Typography, Divider } from 'antd';
import { SettingOutlined, SaveOutlined, SecurityScanOutlined } from '@ant-design/icons';
import { settingsApi } from '@/services/api';

const { Title, Text } = Typography;

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await settingsApi.getSettings();
      form.setFieldsValue(res.data.data);
    } catch (error) {
      message.error('加载配置失败');
    }
  };

  const handleSave = async (values: any) => {
    setLoading(true);
    try {
      await settingsApi.saveSettings(values);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    const webhook = form.getFieldValue('wechat_webhook');
    if (!webhook) {
      message.warning('请先输入 webhook URL');
      return;
    }
    try {
      await settingsApi.testWebhook();
      message.success('测试消息已发送');
    } catch (error) {
      message.error('发送失败');
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <SettingOutlined style={{ fontSize: 24 }} />
        <Title level={2} style={{ margin: 0 }}>🔧 系统设置</Title>
      </Space>

      <Title level={4}>企业微信通知配置</Title>
      <Text type="secondary">
        配置企业微信机器人 Webhook，实现任务通知推送
      </Text>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        style={{ maxWidth: 600, marginTop: 24 }}
      >
        <Form.Item
          name="wechat_webhook"
          label="企业微信机器人 Webhook URL"
          rules={[{ type: 'url', message: '请输入有效的 URL' }]}
          extra="在企业微信中创建群机器人获取 Webhook 地址"
        >
          <Input placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx" size="large" />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              保存配置
            </Button>
            <Button
              icon={<SecurityScanOutlined />}
              onClick={handleTest}
            >
              测试通知
            </Button>
          </Space>
        </Form.Item>
      </Form>

      <Divider />

      <Title level={4}>浏览器配置</Title>
      <Text type="secondary">
        Edge 浏览器路径：C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
      </Text>
      <br />
      <Text type="secondary">
        Edge Driver 路径：项目根目录下的 msedgedriver.exe
      </Text>
    </div>
  );
};

export default Settings;
