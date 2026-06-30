import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const LoadingSpinner = ({ tip = 'Loading...' }) => {
  const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <Spin indicator={antIcon} tip={tip} size="large" />
    </div>
  );
};

export default LoadingSpinner;