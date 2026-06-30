import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Timeline, Tag, Space, Spin } from 'antd';
import { ClockCircleOutlined, UsergroupAddOutlined, MailOutlined, MessageOutlined, IssuesCloseOutlined, TeamOutlined } from '@ant-design/icons';
import { dashboardAPI } from '../../services/api';
import { Line } from '@ant-design/plots';

const DashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);
  const [activityData, setActivityData] = useState([]);
  const [errorData, setErrorData] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [summaryRes, activityRes, errorsRes] = await Promise.all([
        dashboardAPI.getSummary(),
        dashboardAPI.getActivity(),
        dashboardAPI.getErrors()
      ]);

      setSummaryData(summaryRes.data.data);
      setActivityData(activityRes.data.data || []);
      setErrorData(errorsRes.data.data || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock chart data for demonstration
  const loopStatisticsData = [
    { time: '00:00', loops: 2 },
    { time: '04:00', loops: 1 },
    { time: '08:00', loops: 5 },
    { time: '12:00', loops: 8 },
    { time: '16:00', loops: 6 },
    { time: '20:00', loops: 4 },
    { time: '24:00', loops: 3 },
  ];

  const candidateGrowthData = [
    { date: '2023-01', count: 10 },
    { date: '2023-02', count: 25 },
    { date: '2023-03', count: 38 },
    { date: '2023-04', count: 52 },
    { date: '2023-05', count: 61 },
    { date: '2023-06', count: 78 },
  ];

  // Format timeline items
  const timelineItems = activityData.map((item, index) => ({
    children: (
      <div>
        <div>{item.time}</div>
        <div>{item.type} - {item.message}</div>
        {item.details && (
          <div style={{ fontSize: '12px', color: '#888' }}>
            {JSON.stringify(item.details)}
          </div>
        )}
      </div>
    ),
    color: item.type === 'loop' ? 'blue' : item.type === 'search' ? 'green' : 'red',
  }));

  // Format error table columns
  const errorColumns = [
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'resolved' ? 'green' : 'red'}>
          {status || 'open'}
        </Tag>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>
      
      {/* System Status Card */}
      <Card className="dashboard-card">
        <Row gutter={16}>
          <Col span={4}>
            <Statistic 
              title="Recruiting Agent" 
              value="Running" 
              valueStyle={{ color: '#3f8600' }}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={4}>
            <Statistic 
              title="Scheduler" 
              value="Running" 
              valueStyle={{ color: '#3f8600' }}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={4}>
            <Statistic 
              title="Database" 
              value="Connected" 
              valueStyle={{ color: '#3f8600' }}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={4}>
            <Statistic 
              title="GitHub API" 
              value="Connected" 
              valueStyle={{ color: '#3f8600' }}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={4}>
            <Statistic 
              title="SMTP" 
              value="Connected" 
              valueStyle={{ color: '#3f8600' }}
              prefix={<ClockCircleOutlined />}
            />
          </Col>
          <Col span={4}>
            <Statistic 
              title="Running Positions" 
              value={summaryData?.running_positions || 0} 
              prefix={<TeamOutlined />}
            />
          </Col>
        </Row>
      </Card>

      {/* Today's Metrics */}
      <Card className="dashboard-card">
        <Row gutter={16}>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Loops</div>
              <div className="statistic-value">{summaryData?.today_loops || 0}</div>
            </div>
          </Col>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Candidates</div>
              <div className="statistic-value">{summaryData?.today_candidates || 0}</div>
            </div>
          </Col>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Emails</div>
              <div className="statistic-value">{summaryData?.today_emails || 0}</div>
            </div>
          </Col>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Replies</div>
              <div className="statistic-value">{summaryData?.today_replies || 0}</div>
            </div>
          </Col>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Errors</div>
              <div className="statistic-value" style={{ color: '#ff4d4f' }}>{summaryData?.today_errors || 0}</div>
            </div>
          </Col>
          <Col span={4}>
            <div className="statistic-item">
              <div className="statistic-title">Running Positions</div>
              <div className="statistic-value">{summaryData?.running_positions || 0}</div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* Running Positions Table */}
      <Card title="Running Positions" className="dashboard-card">
        <Table
          columns={[
            {
              title: 'Position',
              dataIndex: 'title',
              key: 'title',
            },
            {
              title: 'Status',
              dataIndex: 'status',
              key: 'status',
              render: (status) => (
                <Tag color={status === 'active' ? 'green' : status === 'paused' ? 'orange' : 'red'}>
                  {status}
                </Tag>
              ),
            },
            {
              title: 'Candidates',
              dataIndex: 'candidateCount',
              key: 'candidateCount',
            },
            {
              title: 'Contacted',
              dataIndex: 'contacted',
              key: 'contacted',
            },
            {
              title: 'Last Loop',
              dataIndex: 'lastLoop',
              key: 'lastLoop',
            },
            {
              title: 'Next Loop',
              dataIndex: 'nextLoop',
              key: 'nextLoop',
            },
          ]}
          dataSource={[
            {
              key: '1',
              title: 'Backend Engineer',
              company: 'OpenAI',
              status: 'active',
              candidateCount: 24,
              contacted: 8,
              lastLoop: '2023-06-30 10:30',
              nextLoop: '2023-06-30 11:30',
            },
            {
              key: '2',
              title: 'Frontend Developer',
              company: 'Google',
              status: 'active',
              candidateCount: 18,
              contacted: 5,
              lastLoop: '2023-06-30 09:45',
              nextLoop: '2023-06-30 10:45',
            },
          ]}
          pagination={false}
        />
      </Card>

      <Row gutter={16}>
        {/* Today's Activity */}
        <Col span={12}>
          <Card title="Today's Activity" className="dashboard-card">
            <Timeline items={timelineItems} />
          </Card>
        </Col>

        {/* Recent Errors */}
        <Col span={12}>
          <Card title="Recent Errors" className="dashboard-card">
            <Table
              columns={errorColumns}
              dataSource={errorData}
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Loop Statistics Chart */}
      <Card title="Loop Statistics" className="dashboard-card">
        <Line
          data={loopStatisticsData}
          xField="time"
          yField="loops"
          height={300}
          point={{ size: 5 }}
          tooltip={{ formatter: (datum) => ({ name: 'Loops', value: datum.loops }) }}
        />
      </Card>
    </div>
  );
};

export default DashboardPage;