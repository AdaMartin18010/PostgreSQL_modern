//! 并发控制决策助手 - 后端服务
//!
//! 提供RESTful API，支持并发控制方案推荐、性能预测等功能

use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tracing::{info, warn};

mod decision_engine;
mod predictor;
mod types;

use decision_engine::DecisionEngine;
use types::*;

/// 应用状态
#[derive(Clone)]
struct AppState {
    decision_engine: Arc<DecisionEngine>,
}

/// 健康检查
async fn health_check() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "service": "decision-assistant",
        "version": "0.1.0-alpha"
    }))
}

/// 获取推荐方案
async fn recommend(
    State(state): State<AppState>,
    Json(request): Json<RecommendationRequest>,
) -> Result<Json<RecommendationResponse>, StatusCode> {
    info!("收到推荐请求: {:?}", request);

    let recommendation = state
        .decision_engine
        .recommend(&request)
        .map_err(|e| {
            warn!("推荐失败: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    Ok(Json(RecommendationResponse {
        recommendation,
        timestamp: chrono::Utc::now(),
    }))
}

/// 性能预测
async fn predict(
    State(state): State<AppState>,
    Json(request): Json<PredictionRequest>,
) -> Result<Json<PredictionResponse>, StatusCode> {
    info!("收到预测请求: {:?}", request);

    let prediction = state
        .decision_engine
        .predict_performance(&request)
        .map_err(|e| {
            warn!("预测失败: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    Ok(Json(PredictionResponse {
        prediction,
        timestamp: chrono::Utc::now(),
    }))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 初始化日志
    tracing_subscriber::fmt()
        .with_env_filter("decision_assistant=info,tower_http=info")
        .init();

    info!("🚀 启动并发控制决策助手后端服务...");

    // 初始化决策引擎
    let decision_engine = Arc::new(DecisionEngine::new()?);

    let app_state = AppState { decision_engine };

    // 构建路由
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/v1/recommend", post(recommend))
        .route("/api/v1/predict", post(predict))
        .layer(CorsLayer::permissive())
        .with_state(app_state);

    // 启动服务器
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await?;
    info!("✅ 服务器启动在 http://0.0.0.0:8080");
    info!("📚 API文档: http://localhost:8080/docs");

    axum::serve(listener, app).await?;

    Ok(())
}
