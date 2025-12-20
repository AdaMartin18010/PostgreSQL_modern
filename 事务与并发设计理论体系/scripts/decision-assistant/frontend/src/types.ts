// 类型定义（与后端保持一致）

export interface RecommendationRequest {
  scenario: {
    type: string;
    sub_type?: string;
  };
  requirements: {
    concurrent_users?: number;
    peak_qps?: number;
    consistency: string;
    availability_target?: number;
    latency_target_p99?: number;
  };
  workload: {
    read_write_ratio: string;
    transaction_size?: string;
    hot_spot?: boolean;
    data_size?: string;
  };
  infrastructure?: {
    database?: string;
    cpu_cores?: number;
    memory_gb?: number;
    storage_type?: string;
    network?: string;
  };
}

export interface RecommendationResponse {
  recommendation: {
    isolation_level: string;
    concurrency_control: {
      type: string;
      implementation: string;
      retry_strategy?: string;
    };
    caching?: {
      layer: string;
      strategy: string;
      ttl?: number;
    };
    rationale: Array<{
      decision: string;
      reason: string;
      tradeoff?: string;
    }>;
    alternatives: Array<{
      approach: string;
      pros: string;
      cons: string;
      when_to_use: string;
    }>;
  };
  timestamp: string;
}
