import React from 'react';
import { Card, Tag, Space, Progress, Button, Statistic } from 'antd';
import { TeamOutlined, MailOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';

const PositionCard = ({ position, onEdit, onViewDetails }) => {
  const { 
    title, 
    company, 
    location, 
    status, 
    candidate_count = 0, 
    contacted_count = 0, 
    loop_interval, 
    last_loop_at, 
    next_loop_at 
  } = position;

  // Calculate contact rate percentage
  const contactRate = candidate_count > 0 ? Math.round((contacted_count / candidate_count) * 100) : 0;

  return (
    <Card 
      title={
        <div>
          <div style={{ fontSize: '16px', fontWeight: 'bold' }}>{title}</div>
          <div style={{ fontSize: '14px', color: '#888' }}>{company}</div>
        </div>
      }
      extra={
        <Tag 
          color={status === 'active' ? 'green' : status === 'paused' ? 'orange' : 'red'}
        >
          {status}
        </Tag>
      }
      style={{ marginBottom: 16 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <div><strong>Location:</strong> {location || 'N/A'}</div>
          <div><strong>Loop Interval:</strong> {loop_interval} min</div>
          <div><strong>Last Loop:</strong> {last_loop_at || 'Never'}</div>
          <div><strong>Next Loop:</strong> {next_loop_at || 'N/A'}</div>
        </div>
        <div>
          <Statistic title="Total Candidates" value={candidate_count} prefix={<TeamOutlined />} />
          <Statistic title="Contacted" value={contacted_count} prefix={<MailOutlined />} />
          <div style={{ marginTop: 8 }}>
            <div style={{ marginBottom: 4 }}><strong>Contact Rate: {contactRate}%</strong></div>
            <Progress percent={contactRate} size="small" />
          </div>
        </div>
      </div>
      
      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <Space>
          <Button onClick={() => onViewDetails && onViewDetails(position)}>View Details</Button>
          <Button type="primary" onClick={() => onEdit && onEdit(position)}>Edit</Button>
        </Space>
      </div>
    </Card>
  );
};

export default PositionCard;