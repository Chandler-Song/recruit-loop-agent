import React from 'react';
import { Table, Tag, Space, Button } from 'antd';
import { EditOutlined } from '@ant-design/icons';

const CandidateTable = ({ candidates, loading, onEdit }) => {
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => (a.name || '').localeCompare(b.name || ''),
    },
    {
      title: 'GitHub',
      dataIndex: 'github_login',
      key: 'github_login',
      render: (login, record) => (
        <a href={record.profile_url} target="_blank" rel="noopener noreferrer">
          {login}
        </a>
      ),
    },
    {
      title: 'Company',
      dataIndex: 'company',
      key: 'company',
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source) => (
        <Tag color={source === 'github' ? 'blue' : 'green'}>{source}</Tag>
      ),
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      sorter: (a, b) => (a.score || 0) - (b.score || 0),
      render: (score) => score !== undefined ? score.toFixed(1) : 'N/A',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onEdit && onEdit(record)}
          >
            Edit
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={candidates}
      rowKey="id"
      loading={loading}
      pagination={{ pageSize: 20 }}
    />
  );
};

export default CandidateTable;