import React, { useState, useEffect } from 'react';
import { Table, Input, Button, Space, Tag, DatePicker, Select } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { outreachAPI } from '../../services/api';

const { RangePicker } = DatePicker;
const { Option } = Select;

const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filters, setFilters] = useState({
    keyword: '',
    status: '',
    startDate: null,
    endDate: null,
  });

  useEffect(() => {
    fetchLogs();
  }, [pagination.current, pagination.pageSize, filters]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
      };
      
      // Mock data for now
      const mockLogs = [
        {
          key: '1',
          id: 'log-001',
          time: '2023-06-30 10:30:22',
          module: 'Scheduler',
          message: 'Position Backend Engineer loop started',
          status: 'info',
        },
        {
          key: '2',
          id: 'log-002',
          time: '2023-06-30 10:31:45',
          module: 'Search',
          message: 'GitHub search completed, found 25 candidates',
          status: 'success',
        },
        {
          key: '3',
          id: 'log-003',
          time: '2023-06-30 10:32:10',
          module: 'Dedup',
          message: 'Removed 3 duplicate candidates',
          status: 'info',
        },
        {
          key: '4',
          id: 'log-004',
          time: '2023-06-30 10:33:30',
          module: 'Score',
          message: 'Completed scoring 22 candidates',
          status: 'success',
        },
        {
          key: '5',
          id: 'log-005',
          time: '2023-06-30 10:35:15',
          module: 'Outreach',
          message: 'Sent emails to 5 top candidates',
          status: 'success',
        },
        {
          key: '6',
          id: 'log-006',
          time: '2023-06-30 10:35:20',
          module: 'Outreach',
          message: 'Failed to send email to candidate: Connection timeout',
          status: 'error',
        },
        {
          key: '7',
          id: 'log-007',
          time: '2023-06-30 10:40:05',
          module: 'Scheduler',
          message: 'Position Backend Engineer loop finished',
          status: 'info',
        },
        {
          key: '8',
          id: 'log-008',
          time: '2023-06-30 11:00:00',
          module: 'GitHub API',
          message: 'Rate limit exceeded, pausing for 1 hour',
          status: 'warning',
        },
      ];

      setLogs(mockLogs);
      setPagination(prev => ({
        ...prev,
        total: mockLogs.length,
      }));
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const columns = [
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
      sorter: (a, b) => new Date(a.time) - new Date(b.time),
    },
    {
      title: 'Module',
      dataIndex: 'module',
      key: 'module',
      filters: [
        { text: 'Scheduler', value: 'Scheduler' },
        { text: 'Search', value: 'Search' },
        { text: 'Dedup', value: 'Dedup' },
        { text: 'Score', value: 'Score' },
        { text: 'Outreach', value: 'Outreach' },
        { text: 'GitHub API', value: 'GitHub API' },
      ],
      onFilter: (value, record) => record.module.indexOf(value) === 0,
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
      render: (status) => {
        let color = 'default';
        if (status === 'success') color = 'green';
        if (status === 'error') color = 'red';
        if (status === 'warning') color = 'orange';
        if (status === 'info') color = 'blue';
        return <Tag color={color}>{status}</Tag>;
      },
      filters: [
        { text: 'Info', value: 'info' },
        { text: 'Success', value: 'success' },
        { text: 'Warning', value: 'warning' },
        { text: 'Error', value: 'error' },
      ],
      onFilter: (value, record) => record.status.indexOf(value) === 0,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Input
            placeholder="Search logs"
            prefix={<SearchOutlined />}
            value={filters.keyword}
            onChange={(e) => handleFilterChange('keyword', e.target.value)}
            style={{ width: 300 }}
          />
          <Select
            placeholder="Filter by status"
            allowClear
            style={{ width: 150 }}
            onChange={(value) => handleFilterChange('status', value)}
          >
            <Option value="info">Info</Option>
            <Option value="success">Success</Option>
            <Option value="warning">Warning</Option>
            <Option value="error">Error</Option>
          </Select>
          <RangePicker
            onChange={(dates) => {
              handleFilterChange('startDate', dates ? dates[0] : null);
              handleFilterChange('endDate', dates ? dates[1] : null);
            }}
          />
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={logs}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={handleTableChange}
      />
    </div>
  );
};

export default LogsPage;