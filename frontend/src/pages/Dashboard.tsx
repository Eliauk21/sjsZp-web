import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Typography, Progress, Tag } from 'antd';
import { DashboardOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { taskApi } from '@/services/api';
import type { TaskRecord } from '../../types';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTaskHistory();
  }, []);

  const loadTaskHistory = async () => {
    setLoading(true);
    try {
      const res = await taskApi.getHistory();
      setTasks(res.data.data || []);
    } catch (error) {
      console.error('加载任务历史失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalTasks = tasks.length;
  const successTasks = tasks.filter(t => t.status === 'success').length;
  const failedTasks = tasks.filter(t => t.status === 'failed').length;

  const columns = [
    {
      title: '任务名称',
      dataIndex: 'task_name',
      key: 'task_name',
    },
    {
      title: '操作类型',
      dataIndex: 'operation',
      key: 'operation',
    },
    {
      title: '店铺数',
      dataIndex: 'shop_count',
      key: 'shop_count',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'success' ? 'success' : status === 'failed' ? 'error' : 'processing';
        const icon = status === 'success' ? <CheckCircleOutlined /> : status === 'failed' ? <CloseCircleOutlined /> : null;
        return <Tag color={color} icon={icon}>{status}</Tag>;
      },
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
    },
  ];

  return (
    <div>
      <Title level={2}>📊 数据面板</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="总任务数"
              value={totalTasks}
              prefix={<DashboardOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="成功"
              value={successTasks}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="失败"
              value={failedTasks}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Title level={4}>历史任务记录</Title>
      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="task_id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
};

export default Dashboard;
