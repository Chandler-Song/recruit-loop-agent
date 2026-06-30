import React, { useState, useEffect } from 'react';
import { Tabs, Card, Button, Table, Modal, Form, Input, Select, InputNumber, Tag, Space, message, Spin } from 'antd';
import { EditOutlined, PlayCircleOutlined, PauseCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { positionAPI, candidateAPI, pipelineAPI } from '../../services/api';

const { TabPane } = Tabs;
const { TextArea } = Input;

const PositionDetailPage = () => {
  const [loading, setLoading] = useState(true);
  const [position, setPosition] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [pipelineData, setPipelineData] = useState({});
  const [logs, setLogs] = useState([]);
  const [editing, setEditing] = useState(false);
  const [editForm] = Form.useForm();
  const [showEditModal, setShowEditModal] = useState(false);

  const positionId = '1'; // In a real app, this would come from route params

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Mock data for now
      setPosition({
        id: '1',
        title: 'Backend Engineer',
        company: 'OpenAI',
        description: 'Looking for experienced backend engineers with Python and FastAPI expertise.',
        location: 'Remote',
        requiredSkills: ['Python', 'FastAPI', 'SQLAlchemy'],
        searchKeywords: ['Backend Developer', 'Python'],
        status: 'active',
        loopInterval: 60,
        lastLoopAt: '2023-06-30 10:30',
        nextLoopAt: '2023-06-30 11:30',
        candidateCount: 24,
        contactedCount: 8,
      });

      setCandidates([
        {
          key: '1',
          name: 'John Doe',
          score: 92,
          skills: ['Python', 'FastAPI', 'SQLAlchemy'],
          company: 'Tech Corp',
          email: 'john@example.com',
          source: 'GitHub',
        },
        {
          key: '2',
          name: 'Jane Smith',
          score: 87,
          skills: ['Python', 'Django', 'PostgreSQL'],
          company: 'Startup Inc',
          email: 'jane@example.com',
          source: 'GitHub',
        },
      ]);

      setPipelineData({
        discovered: [
          {
            id: '1',
            name: 'John Doe',
            score: 92,
            status: 'discovered',
            lastContact: '2023-06-29',
          },
          {
            id: '2',
            name: 'Bob Johnson',
            score: 78,
            status: 'discovered',
            lastContact: '2023-06-28',
          },
        ],
        contacted: [
          {
            id: '3',
            name: 'Alice Williams',
            score: 85,
            status: 'contacted',
            lastContact: '2023-06-30',
          },
        ],
        replied: [
          {
            id: '4',
            name: 'Charlie Brown',
            score: 90,
            status: 'replied',
            lastContact: '2023-06-29',
          },
        ],
        interview: [],
        offer: [],
        rejected: [
          {
            id: '5',
            name: 'David Wilson',
            score: 70,
            status: 'rejected',
            lastContact: '2023-06-25',
          },
        ],
      });

      setLogs([
        {
          key: '1',
          time: '2023-06-30 10:30',
          node: 'Search',
          status: 'success',
          duration: '1200ms',
          error: null,
        },
        {
          key: '2',
          time: '2023-06-30 10:32',
          node: 'Dedup',
          status: 'success',
          duration: '300ms',
          error: null,
        },
        {
          key: '3',
          time: '2023-06-30 10:33',
          node: 'Score',
          status: 'success',
          duration: '800ms',
          error: null,
        },
      ]);
    } catch (error) {
      console.error('Failed to fetch position data:', error);
      message.error('Failed to load position data');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    if (position) {
      editForm.setFieldsValue({
        title: position.title,
        company: position.company,
        description: position.description,
        location: position.location,
        requiredSkills: position.requiredSkills.join(', '),
        searchKeywords: position.searchKeywords.join(', '),
        loopInterval: position.loopInterval,
      });
      setShowEditModal(true);
    }
  };

  const handleSave = async () => {
    try {
      const values = await editForm.validateFields();
      
      // Format skills and keywords back to arrays
      const updatedPosition = {
        ...values,
        requiredSkills: values.requiredSkills.split(',').map(s => s.trim()).filter(s => s),
        searchKeywords: values.searchKeywords.split(',').map(s => s.trim()).filter(s => s),
      };
      
      // In a real app, we would call the API to update the position
      // await positionAPI.update(positionId, updatedPosition);
      
      message.success('Position updated successfully');
      setShowEditModal(false);
      setEditing(false);
      
      // Refresh data
      fetchData();
    } catch (error) {
      console.error('Failed to save position:', error);
      message.error('Failed to save position');
    }
  };

  const handleStatusChange = async (action) => {
    try {
      if (action === 'pause') {
        // await positionAPI.pause(positionId);
        message.success('Position paused');
      } else if (action === 'resume') {
        // await positionAPI.resume(positionId);
        message.success('Position resumed');
      } else if (action === 'close') {
        // await positionAPI.close(positionId);
        message.success('Position closed');
      }
      
      // Refresh data
      fetchData();
    } catch (error) {
      console.error(`Failed to ${action} position:`, error);
      message.error(`Failed to ${action} position`);
    }
  };

  const candidateColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      sorter: (a, b) => a.score - b.score,
    },
    {
      title: 'Skills',
      dataIndex: 'skills',
      key: 'skills',
      render: (skills) => (
        <Space wrap>
          {skills.map(skill => (
            <Tag key={skill} color="blue">{skill}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Company',
      dataIndex: 'company',
      key: 'company',
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
    },
  ];

  const logColumns = [
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
    },
    {
      title: 'Node',
      dataIndex: 'node',
      key: 'node',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>{status}</Tag>
      ),
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: 'Error',
      dataIndex: 'error',
      key: 'error',
      render: (error) => error ? <Tag color="red">{error}</Tag> : '-',
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!position) {
    return <div>Position not found</div>;
  }

  const kanbanColumns = [
    { key: 'discovered', title: 'Discovered', color: '#1890ff' },
    { key: 'contacted', title: 'Contacted', color: '#52c41a' },
    { key: 'replied', title: 'Replied', color: '#faad14' },
    { key: 'interview', title: 'Interview', color: '#722ed1' },
    { key: 'offer', title: 'Offer', color: '#13c2c2' },
    { key: 'rejected', title: 'Rejected', color: '#f5222d' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>{position.title} - {position.company}</h1>
        <Space>
          <Tag color={position.status === 'active' ? 'green' : position.status === 'paused' ? 'orange' : 'red'}>
            {position.status}
          </Tag>
          <Button icon={<EditOutlined />} onClick={handleEdit}>Edit</Button>
          <Button icon={<PlayCircleOutlined />} onClick={() => handleStatusChange('resume')} disabled={position.status !== 'paused'}>Resume</Button>
          <Button icon={<PauseCircleOutlined />} onClick={() => handleStatusChange('pause')} disabled={position.status !== 'active'}>Pause</Button>
          <Button icon={<CloseCircleOutlined />} onClick={() => handleStatusChange('close')} danger>Close</Button>
        </Space>
      </div>

      <Tabs defaultActiveKey="overview">
        <TabPane tab="Overview" key="overview">
          <Card title="Position Details">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
              <div><strong>Title:</strong> {position.title}</div>
              <div><strong>Company:</strong> {position.company}</div>
              <div><strong>Status:</strong> <Tag color={position.status === 'active' ? 'green' : position.status === 'paused' ? 'orange' : 'red'}>{position.status}</Tag></div>
              <div><strong>Location:</strong> {position.location}</div>
              <div><strong>Loop Interval:</strong> {position.loopInterval} minutes</div>
              <div><strong>Last Loop:</strong> {position.lastLoopAt}</div>
              <div><strong>Next Loop:</strong> {position.nextLoopAt}</div>
              <div><strong>Candidate Count:</strong> {position.candidateCount}</div>
              <div><strong>Contacted:</strong> {position.contactedCount}</div>
            </div>
            <div style={{ marginTop: 16 }}>
              <strong>Description:</strong>
              <div>{position.description}</div>
            </div>
            <div style={{ marginTop: 16 }}>
              <strong>Required Skills:</strong>
              <Space wrap style={{ marginTop: 8 }}>
                {position.requiredSkills.map(skill => (
                  <Tag key={skill} color="blue">{skill}</Tag>
                ))}
              </Space>
            </div>
            <div style={{ marginTop: 16 }}>
              <strong>Search Keywords:</strong>
              <Space wrap style={{ marginTop: 8 }}>
                {position.searchKeywords.map(keyword => (
                  <Tag key={keyword}>{keyword}</Tag>
                ))}
              </Space>
            </div>
          </Card>
        </TabPane>

        <TabPane tab="Candidates" key="candidates">
          <Card>
            <Table 
              columns={candidateColumns} 
              dataSource={candidates} 
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        <TabPane tab="Pipeline" key="pipeline">
          <Card>
            <div style={{ display: 'flex', overflowX: 'auto' }}>
              {kanbanColumns.map(col => (
                <div key={col.key} className="kanban-column" style={{ borderLeft: `4px solid ${col.color}` }}>
                  <h3>{col.title} ({pipelineData[col.key]?.length || 0})</h3>
                  {(pipelineData[col.key] || []).map(item => (
                    <div key={item.id} className={`kanban-item pipeline-status-${col.key}`}>
                      <div><strong>{item.name}</strong></div>
                      <div>Score: {item.score}</div>
                      <div>Last Contact: {item.lastContact}</div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </Card>
        </TabPane>

        <TabPane tab="Logs" key="logs">
          <Card>
            <Table 
              columns={logColumns} 
              dataSource={logs} 
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title="Edit Position"
        open={showEditModal}
        onCancel={() => setShowEditModal(false)}
        onOk={handleSave}
        width={800}
      >
        <Form
          form={editForm}
          layout="vertical"
        >
          <Form.Item
            name="title"
            label="Position Title"
            rules={[{ required: true, message: 'Please enter position title' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="company"
            label="Company"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Description"
          >
            <TextArea rows={4} />
          </Form.Item>
          
          <Form.Item
            name="location"
            label="Location"
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            name="requiredSkills"
            label="Required Skills (comma separated)"
          >
            <Input placeholder="e.g., Python, FastAPI, SQLAlchemy" />
          </Form.Item>
          
          <Form.Item
            name="searchKeywords"
            label="Search Keywords (comma separated)"
          >
            <Input placeholder="e.g., Backend Developer, Python" />
          </Form.Item>
          
          <Form.Item
            name="loopInterval"
            label="Loop Interval (minutes)"
            rules={[{ required: true, message: 'Please enter loop interval' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PositionDetailPage;