import React, { useState } from 'react';
import { Button, Space, message, Typography, Progress } from 'antd';
import { FrownOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { taskApi } from '@/services/api';

const { Title } = Typography;

const TaskCreateV4: React.FC = () => {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleExecute = async () => {
    setRunning(true);
    setProgress(10);
    try {
      await taskApi.execute('edit_old_module', {});
      message.success('v4 模块创建完成');
      setProgress(100);
    } catch (error) {
      message.error('创建失败');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        {/*<FrownOutlined style={{ fontSize: 24 }} />*/}
        <Title level={2} style={{ margin: 0 }}>🆕 创建 v4 版本模块</Title>
      </Space>

      <Typography.Text type="secondary">
        编辑高版本模块（v4 版本）
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

      {running && (
        <Progress percent={progress} status="active" />
      )}
    </div>
  );
};

export default TaskCreateV4;
