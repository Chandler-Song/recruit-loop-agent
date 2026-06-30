import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, message, Popconfirm } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { schedulerAPI } from '../../services/api';

const SchedulerPage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      // Mock data for now - in real app, we would call schedulerAPI.getJobs()
      setJobs([
        {
          key: '1',
          position: 'Backend Engineer',
          company: 'OpenAI',
          status: 'running',
          running: true,
          lastRun: '2023-06-30 10:30',
          duration: '1200ms',
          nextRun: '2023-06-30 11:30',
          loopCount: 42,
        },
        {
          key: '2',
          position: 'Frontend Developer',
          company: 'Google',
          status: 'waiting',
          running: false,
          lastRun: '2023-06-30 09:45',
          duration: '800ms',
          nextRun: '2023-06-30 10:45',
          loopCount: 38,
        },
        {
          key: '3',
          position: 'DevOps Engineer',
          company: 'Amazon',
          status: 'paused',
          running: false,
          lastRun: '2023-06-30 08:15',
          duration: '1500ms',
          nextRun: 'Paused',
          loopCount: 25,
        },
      ]);
    } catch (error) {
      message.error('Failed to fetch scheduler jobs');
      console.error('Failed to fetch scheduler jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunNow = async (positionId) => {
    try {
      // In real app: await schedulerAPI.runNow(positionId);
      message.success('Job started successfully');
      fetchJobs(); // Refresh the list
    } catch (error) {
      message.error('Failed to run job');
    }
  };

  const handlePause = async (positionId) => {
    try {
      // In real app: await schedulerAPI.pause(positionId);
      message.success('Job paused successfully');
      fetchJobs(); // Refresh the list
    } catch (error) {
      message.error('Failed to pause job');
    }
  };

  const handleResume = async (positionId) => {
    try {
      // In real app: await schedulerAPI.resume(positionId);
      message.success('Job resumed successfully');
      fetchJobs(); // Refresh the list
    } catch (error) {
      message.error('Failed to resume job');
    }
  };

  const columns = [
    {
      title: 'Position',
      dataIndex: 'position',
      key: 'position',
    },
    {
      title: 'Company',
      dataIndex: 'company',
      key: 'company',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'default';
        if (status === 'running') color = 'green';
        if (status === 'waiting') color = 'blue';
        if (status === 'paused') color = 'orange';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Running',
      dataIndex: 'running',
      key: 'running',
      render: (running) => (
        <Tag color={running ? 'green' : 'red'}>
          {running ? 'Yes' : 'No'}
        </Tag>
      ),
    },
    {
      title: 'Last Run',
      dataIndex: 'lastRun',
      key: 'lastRun',
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: 'Next Run',
      dataIndex: 'nextRun',
      key: 'nextRun',
    },
    {
      title: 'Loop Count',
      dataIndex: 'loopCount',
      key: 'loopCount',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={() => handleRunNow(record.key)}
            disabled={record.status === 'running'}
          >
            Run Now
          </Button>
          {record.status === 'paused' ? (
            <Button
              type="default"
              icon={<PlayCircleOutlined />}
              onClick={() => handleResume(record.key)}
            >
              Resume
            </Button>
          ) : (
            <Popconfirm
              title="Are you sure you want to pause this job?"
              onConfirm={() => handlePause(record.key)}
            >
              <Button
                type="default"
                icon={<PauseCircleOutlined />}
                danger
              >
                Pause
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h1>Scheduler</h1>
        <p>Monitor and manage recruiting loop schedules</p>
      </div>

      <Table
        columns={columns}
        dataSource={jobs}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
};

export default SchedulerPage;