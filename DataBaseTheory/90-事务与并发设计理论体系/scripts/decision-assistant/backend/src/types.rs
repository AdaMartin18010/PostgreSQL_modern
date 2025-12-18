//! 类型定义

use serde::{Deserialize, Serialize};

/// 推荐请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecommendationRequest {
    pub scenario: ScenarioConfig,
    pub requirements: Requirements,
    pub workload: WorkloadConfig,
    pub infrastructure: Option<InfrastructureConfig>,
}

/// 场景配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioConfig {
    pub r#type: String,  // "e-commerce", "financial", "social", "analytics"
    pub sub_type: Option<String>,  // "seckill", "payment", etc.
}

/// 需求配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Requirements {
    pub concurrent_users: Option<u64>,
    pub peak_qps: Option<u64>,
    pub consistency: String,  // "strong", "relaxed", "eventual"
    pub availability_target: Option<f64>,  // 99.9, 99.99, etc.
    pub latency_target_p99: Option<u64>,  // milliseconds
}

/// 工作负载配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkloadConfig {
    pub read_write_ratio: String,  // "9:1", "1:1", etc.
    pub transaction_size: Option<String>,  // "small", "medium", "large"
    pub hot_spot: Option<bool>,
    pub data_size: Option<String>,
}

/// 基础设施配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InfrastructureConfig {
    pub database: Option<String>,
    pub cpu_cores: Option<u32>,
    pub memory_gb: Option<u32>,
    pub storage_type: Option<String>,
    pub network: Option<String>,
}

/// 推荐响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecommendationResponse {
    pub recommendation: Recommendation,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// 推荐方案
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recommendation {
    pub isolation_level: String,
    pub concurrency_control: ConcurrencyControl,
    pub caching: Option<CachingStrategy>,
    pub database_config: Option<DatabaseConfig>,
    pub rationale: Vec<DecisionReason>,
    pub alternatives: Vec<Alternative>,
    pub code_templates: Option<CodeTemplates>,
}

/// 并发控制策略
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConcurrencyControl {
    pub r#type: String,  // "Optimistic Locking", "Pessimistic Locking", "MVCC"
    pub implementation: String,
    pub retry_strategy: Option<String>,
}

/// 缓存策略
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachingStrategy {
    pub layer: String,  // "Redis", "Memcached"
    pub strategy: String,
    pub ttl: Option<u64>,
}

/// 数据库配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub shared_buffers: Option<String>,
    pub work_mem: Option<String>,
    pub max_connections: Option<u32>,
    pub synchronous_commit: Option<String>,
}

/// 决策理由
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DecisionReason {
    pub decision: String,
    pub reason: String,
    pub tradeoff: Option<String>,
}

/// 替代方案
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alternative {
    pub approach: String,
    pub pros: String,
    pub cons: String,
    pub when_to_use: String,
}

/// 代码模板
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeTemplates {
    pub rust: Option<String>,
    pub java: Option<String>,
    pub python: Option<String>,
}

/// 预测请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PredictionRequest {
    pub solution: Recommendation,
    pub infrastructure: InfrastructureConfig,
    pub workload: WorkloadConfig,
}

/// 预测响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PredictionResponse {
    pub prediction: PerformancePrediction,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// 性能预测
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformancePrediction {
    pub expected_tps: u64,
    pub expected_avg_latency_ms: f64,
    pub expected_p99_latency_ms: f64,
    pub confidence: f64,
    pub resource_usage: Option<ResourceUsage>,
}

/// 资源使用
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceUsage {
    pub cpu_percent: f64,
    pub memory_gb: f64,
    pub disk_io_mbps: f64,
}
