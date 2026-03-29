import React, { useState } from 'react';
import { Button, Space, message, Typography, Progress } from 'antd';
import { SearchOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi } from '@/services/api';

const { Title } = Typography;

const TaskCheckModule: React.FC = () => {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleExecute = async () => {
    setRunning(true);
    setProgress(10);
    try {
      await taskApi.execute('delete_fail_module', {});
      message.success('模块检查完成');
      setProgress(100);
    } catch (error) {
      message.error('检查失败');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <SearchOutlined style={{ fontSize: 24 }} />
        <Title level={2} style={{ margin: 0 }}>🔍 模块状态检查</Title>
      </Space>

      <Typography.Text type="secondary">
        检查新增店铺模块的创建情况，删除打包失败的模块并重新创建
      </Typography.Text>

      <Space style={{ margin: '16px 0' }}>
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={running}
        >
          开始检查
        </Button>
      </Space>

      {running && (
        <Progress percent={progress} status="active" />
      )}
    </div>
  );
};

export default TaskCheckModule;
