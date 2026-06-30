import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Tag,
  Popconfirm,
  message,
  InputNumber,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { positionAPI } from '../../services/api';

const { Option } = Select;

const PositionsPage = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPosition, setEditingPosition] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchPositions();
  }, []);

  const fetchPositions = async () => {
    setLoading(true);
    try {
      const response = await positionAPI.getAll();
      setPositions(response.data.data || response.data);
    } catch (error) {
      message.error('Failed to fetch positions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrUpdate = async (values) => {
    try {
      if (editingPosition) {
        await positionAPI.update(editingPosition.id, values);
        message.success('Position updated successfully');
      } else {
        await positionAPI.create(values);
        message.success('Position created successfully');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingPosition(null);
      fetchPositions();
    } catch (error) {
      message.error('Operation failed');
    }
  };

  const handleDelete = async (id) => {
    try {
      await positionAPI.delete(id);
      message.success('Position deleted successfully');
      fetchPositions();
    } catch (error) {
      message.error('Failed to delete position');
    }
  };

  const handleStatusChange = async (id, action) => {
    try {
      if (action === 'pause') {
        await positionAPI.pause(id);
        message.success('Position paused successfully');
      } else if (action === 'resume') {
        await positionAPI.resume(id);
        message.success('Position resumed successfully');
      } else if (action === 'close') {
        await positionAPI.close(id);
        message.success('Position closed successfully');
      }
      fetchPositions();
    } catch (error) {
      message.error(`Failed to ${action} position`);
    }
  };

  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Company',
      dataIndex: 'company',
      key: 'company',
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'default';
        if (status === 'active') color = 'green';
        if (status === 'paused') color = 'orange';
        if (status === 'closed') color = 'red';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Candidates',
      dataIndex: 'candidate_count',
      key: 'candidate_count',
      render: (_, record) => record.candidate_count || 0,
    },
    {
      title: 'Loop Interval (min)',
      dataIndex: 'loop_interval',
      key: 'loop_interval',
    },
    {
      title: 'Last Loop',
      dataIndex: 'last_loop_at',
      key: 'last_loop_at',
      render: (date) => date ? new Date(date).toLocaleString() : 'Never',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            onClick={() => {
              setEditingPosition(record);
              form.setFieldsValue({
                title: record.title,
                company: record.company,
                description: record.description,
                location: record.location,
                required_skills: record.required_skills ? record.required_skills.join(',') : '',
                search_keywords: record.search_keywords ? record.search_keywords.join(',') : '',
                loop_interval: record.loop_interval,
              });
              setModalVisible(true);
            }}
          >
            <EditOutlined />
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this position?"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger>
              <DeleteOutlined />
            </Button>
          </Popconfirm>
          {record.status === 'active' && (
            <Popconfirm
              title="Are you sure you want to pause this position?"
              onConfirm={() => handleStatusChange(record.id, 'pause')}
            >
              <Button type="link" danger>
                <PauseCircleOutlined />
              </Button>
            </Popconfirm>
          )}
          {record.status === 'paused' && (
            <Popconfirm
              title="Are you sure you want to resume this position?"
              onConfirm={() => handleStatusChange(record.id, 'resume')}
            >
              <Button type="link" type="primary">
                <PlayCircleOutlined />
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  const onFinish = (values) => {
    // Convert comma separated strings to arrays
    if (values.required_skills) {
      values.required_skills = values.required_skills.split(',').map(skill => skill.trim()).filter(skill => skill);
    }
    if (values.search_keywords) {
      values.search_keywords = values.search_keywords.split(',').map(keyword => keyword.trim()).filter(keyword => keyword);
    }
    handleCreateOrUpdate(values);
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingPosition(null);
            form.resetFields();
            setModalVisible(true);
          }}
        >
          New Position
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={positions}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editingPosition ? 'Edit Position' : 'Create Position'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingPosition(null);
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: 'Please enter position title' }]}
          >
            <Input placeholder="Enter position title" />
          </Form.Item>

          <Form.Item
            name="company"
            label="Company"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input placeholder="Enter company name" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
          >
            <Input.TextArea rows={4} placeholder="Enter position description" />
          </Form.Item>

          <Form.Item
            name="location"
            label="Location"
          >
            <Input placeholder="Enter location" />
          </Form.Item>

          <Form.Item
            name="required_skills"
            label="Required Skills (comma separated)"
          >
            <Input placeholder="e.g., Python,React,Node.js" />
          </Form.Item>

          <Form.Item
            name="search_keywords"
            label="Search Keywords (comma separated)"
          >
            <Input placeholder="e.g., backend developer,python developer" />
          </Form.Item>

          <Form.Item
            name="loop_interval"
            label="Loop Interval (minutes)"
            rules={[{ required: true, message: 'Please enter loop interval' }]}
          >
            <InputNumber min={1} placeholder="Enter loop interval in minutes" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingPosition ? 'Update' : 'Create'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false);
                form.resetFields();
                setEditingPosition(null);
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PositionsPage;