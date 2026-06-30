import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Space, message, Tabs, Alert } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { systemAPI } from '../../services/api';

const { TabPane } = Tabs;

const SettingsPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState({});

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      // Mock config data for now - in real app we would call systemAPI.getConfig()
      const mockConfig = {
        github_token: 'ghp_xxx...',
        smtp_host: 'smtp.gmail.com',
        smtp_port: 587,
        smtp_username: 'your-email@gmail.com',
        smtp_from: 'your-email@gmail.com',
        max_candidates_per_position: 100,
        search_timeout: 30,
        loop_interval_default: 60,
      };
      setConfig(mockConfig);
      form.setFieldsValue(mockConfig);
    } catch (error) {
      message.error('Failed to fetch system configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values) => {
    setSaving(true);
    try {
      // In real app: await systemAPI.updateConfig(values);
      message.success('Configuration saved successfully');
    } catch (error) {
      message.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1>System Settings</h1>
      <p>Configure system-wide settings for the recruiting agent</p>

      <Alert
        message="Configuration Changes"
        description="Some configuration changes may require a restart of the recruiting agent to take effect."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Tabs defaultActiveKey="general">
        <TabPane tab="General" key="general">
          <Card title="General Settings">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              initialValues={config}
            >
              <Form.Item
                name="loop_interval_default"
                label="Default Loop Interval (minutes)"
                tooltip="Default interval between recruiting loops for new positions"
              >
                <Input placeholder="Enter default loop interval in minutes" />
              </Form.Item>

              <Form.Item
                name="max_candidates_per_position"
                label="Max Candidates Per Position"
                tooltip="Maximum number of candidates to store for each position"
              >
                <Input placeholder="Enter maximum number of candidates" />
              </Form.Item>

              <Form.Item
                name="search_timeout"
                label="Search Timeout (seconds)"
                tooltip="Timeout for each search operation in seconds"
              >
                <Input placeholder="Enter search timeout in seconds" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                    Save General Settings
                  </Button>
                  <Button onClick={fetchConfig}>Reset</Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab="GitHub Integration" key="github">
          <Card title="GitHub API Configuration">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              initialValues={config}
            >
              <Form.Item
                name="github_token"
                label="GitHub Personal Access Token"
                tooltip="Token for accessing GitHub API to search for candidates"
                rules={[
                  {
                    required: true,
                    message: 'Please enter your GitHub personal access token',
                  },
                ]}
              >
                <Input.Password placeholder="Enter your GitHub personal access token" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                    Save GitHub Settings
                  </Button>
                  <Button onClick={fetchConfig}>Reset</Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab="Email Settings" key="email">
          <Card title="Email Configuration">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              initialValues={config}
            >
              <Form.Item
                name="smtp_host"
                label="SMTP Host"
                rules={[
                  {
                    required: true,
                    message: 'Please enter your SMTP host',
                  },
                ]}
              >
                <Input placeholder="e.g., smtp.gmail.com" />
              </Form.Item>

              <Form.Item
                name="smtp_port"
                label="SMTP Port"
                rules={[
                  {
                    required: true,
                    message: 'Please enter your SMTP port',
                  },
                ]}
              >
                <Input placeholder="e.g., 587" />
              </Form.Item>

              <Form.Item
                name="smtp_username"
                label="SMTP Username"
                rules={[
                  {
                    required: true,
                    message: 'Please enter your SMTP username',
                  },
                ]}
              >
                <Input placeholder="e.g., your-email@gmail.com" />
              </Form.Item>

              <Form.Item
                name="smtp_password"
                label="SMTP Password"
                rules={[
                  {
                    required: true,
                    message: 'Please enter your SMTP password',
                  },
                ]}
              >
                <Input.Password placeholder="Enter your SMTP password" />
              </Form.Item>

              <Form.Item
                name="smtp_from"
                label="From Email Address"
                rules={[
                  {
                    type: 'email',
                    message: 'Please enter a valid email address',
                  },
                  {
                    required: true,
                    message: 'Please enter the from email address',
                  },
                ]}
              >
                <Input placeholder="e.g., recruiter@company.com" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={saving} icon={<SaveOutlined />}>
                    Save Email Settings
                  </Button>
                  <Button onClick={fetchConfig}>Reset</Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default SettingsPage;