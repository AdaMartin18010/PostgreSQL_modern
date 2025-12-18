import React, { useState } from 'react';
import { Button, Card, Form, Input, Select, Space, Typography, Divider, Alert } from 'antd';
import axios from 'axios';
import type { RecommendationRequest, RecommendationResponse } from './types';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

function App() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onFinish = async (values: any) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const request: RecommendationRequest = {
        scenario: {
          type: values.scenario_type || 'e-commerce',
          sub_type: values.scenario_sub_type,
        },
        requirements: {
          concurrent_users: values.concurrent_users ? parseInt(values.concurrent_users) : undefined,
          peak_qps: values.peak_qps ? parseInt(values.peak_qps) : undefined,
          consistency: values.consistency || 'relaxed',
          availability_target: values.availability_target ? parseFloat(values.availability_target) : undefined,
          latency_target_p99: values.latency_target_p99 ? parseInt(values.latency_target_p99) : undefined,
        },
        workload: {
          read_write_ratio: values.read_write_ratio || '9:1',
          transaction_size: values.transaction_size,
          hot_spot: values.hot_spot === 'true',
          data_size: values.data_size,
        },
        infrastructure: {
          database: values.database,
          cpu_cores: values.cpu_cores ? parseInt(values.cpu_cores) : undefined,
          memory_gb: values.memory_gb ? parseInt(values.memory_gb) : undefined,
          storage_type: values.storage_type,
          network: values.network,
        },
      };

      const response = await axios.post<RecommendationResponse>(
        `${API_URL}/recommend`,
        request
      );

      setResult(response.data);
    } catch (err: any) {
      setError(err.message || '请求失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={1}>并发控制决策助手</Title>
      <Paragraph>
        根据您的业务需求，自动推荐最适合的并发控制方案
      </Paragraph>

      <Divider />

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            scenario_type: 'e-commerce',
            consistency: 'relaxed',
            read_write_ratio: '9:1',
          }}
        >
          <Title level={3}>场景配置</Title>
          <Form.Item label="场景类型" name="scenario_type">
            <Select>
              <Option value="e-commerce">电商</Option>
              <Option value="financial">金融</Option>
              <Option value="social">社交</Option>
              <Option value="analytics">分析</Option>
            </Select>
          </Form.Item>

          <Form.Item label="子场景" name="scenario_sub_type">
            <Select placeholder="可选">
              <Option value="seckill">秒杀</Option>
              <Option value="payment">支付</Option>
              <Option value="trading">交易</Option>
            </Select>
          </Form.Item>

          <Title level={3}>需求配置</Title>
          <Form.Item label="并发用户数" name="concurrent_users">
            <Input placeholder="例如: 100000" />
          </Form.Item>

          <Form.Item label="峰值QPS" name="peak_qps">
            <Input placeholder="例如: 50000" />
          </Form.Item>

          <Form.Item label="一致性要求" name="consistency">
            <Select>
              <Option value="strong">强一致性</Option>
              <Option value="relaxed">宽松一致性</Option>
              <Option value="eventual">最终一致性</Option>
            </Select>
          </Form.Item>

          <Title level={3}>工作负载</Title>
          <Form.Item label="读写比例" name="read_write_ratio">
            <Select>
              <Option value="9:1">读多写少 (9:1)</Option>
              <Option value="1:1">读写均衡 (1:1)</Option>
              <Option value="1:9">写多读少 (1:9)</Option>
            </Select>
          </Form.Item>

          <Form.Item label="是否有热点数据" name="hot_spot">
            <Select>
              <Option value="true">是</Option>
              <Option value="false">否</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              获取推荐方案
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
          style={{ marginTop: '24px' }}
        />
      )}

      {result && (
        <Card title="推荐方案" style={{ marginTop: '24px' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Title level={4}>隔离级别</Title>
              <Paragraph>{result.recommendation.isolation_level}</Paragraph>
            </div>

            <div>
              <Title level={4}>并发控制策略</Title>
              <Paragraph>
                {result.recommendation.concurrency_control.type} - {result.recommendation.concurrency_control.implementation}
              </Paragraph>
            </div>

            {result.recommendation.caching && (
              <div>
                <Title level={4}>缓存策略</Title>
                <Paragraph>
                  {result.recommendation.caching.layer} - {result.recommendation.caching.strategy}
                </Paragraph>
              </div>
            )}

            <div>
              <Title level={4}>决策理由</Title>
              {result.recommendation.rationale.map((reason, idx) => (
                <Card key={idx} size="small" style={{ marginBottom: '8px' }}>
                  <Paragraph strong>{reason.decision}</Paragraph>
                  <Paragraph>{reason.reason}</Paragraph>
                  {reason.tradeoff && (
                    <Paragraph type="secondary">权衡: {reason.tradeoff}</Paragraph>
                  )}
                </Card>
              ))}
            </div>

            {result.recommendation.alternatives.length > 0 && (
              <div>
                <Title level={4}>替代方案</Title>
                {result.recommendation.alternatives.map((alt, idx) => (
                  <Card key={idx} size="small" style={{ marginBottom: '8px' }}>
                    <Paragraph strong>{alt.approach}</Paragraph>
                    <Paragraph>优点: {alt.pros}</Paragraph>
                    <Paragraph>缺点: {alt.cons}</Paragraph>
                    <Paragraph type="secondary">适用场景: {alt.when_to_use}</Paragraph>
                  </Card>
                ))}
              </div>
            )}
          </Space>
        </Card>
      )}
    </div>
  );
}

export default App;
