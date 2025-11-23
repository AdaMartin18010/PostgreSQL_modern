#!/bin/bash

# PostgreSQL + pgvector 验证脚本
# 验证部署是否成功

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
DB_NAME=${DB_NAME:-vector_db}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PostgreSQL + pgvector 验证脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Docker 容器
check_container() {
    echo -e "${YELLOW}检查 Docker 容器...${NC}"
    
    if docker ps | grep -q postgres-pgvector; then
        echo -e "${GREEN}✓ 容器运行中${NC}"
    else
        echo -e "${RED}✗ 容器未运行${NC}"
        exit 1
    fi
}

# 检查数据库连接
check_connection() {
    echo -e "${YELLOW}检查数据库连接...${NC}"
    
    if docker-compose exec -T postgres-pgvector pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 数据库连接正常${NC}"
    else
        echo -e "${RED}✗ 数据库连接失败${NC}"
        exit 1
    fi
}

# 检查 pgvector 扩展
check_pgvector() {
    echo -e "${YELLOW}检查 pgvector 扩展...${NC}"
    
    result=$(docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
    
    if [ "$result" -eq 1 ]; then
        echo -e "${GREEN}✓ pgvector 扩展已启用${NC}"
    else
        echo -e "${RED}✗ pgvector 扩展未启用${NC}"
        exit 1
    fi
}

# 检查向量类型
check_vector_type() {
    echo -e "${YELLOW}检查向量类型...${NC}"
    
    result=$(docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM pg_type WHERE typname = 'vector';")
    
    if [ "$result" -eq 1 ]; then
        echo -e "${GREEN}✓ 向量类型可用${NC}"
    else
        echo -e "${RED}✗ 向量类型不可用${NC}"
        exit 1
    fi
}

# 测试向量操作
test_vector_operations() {
    echo -e "${YELLOW}测试向量操作...${NC}"
    
    # 创建测试表
    docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} <<EOF > /dev/null 2>&1
-- 创建测试表
CREATE TABLE IF NOT EXISTS test_vectors (
    id SERIAL PRIMARY KEY,
    embedding vector(3)
);

-- 插入测试数据
INSERT INTO test_vectors (embedding) VALUES 
    ('[1,2,3]'::vector),
    ('[4,5,6]'::vector),
    ('[7,8,9]'::vector)
ON CONFLICT DO NOTHING;

-- 测试相似度查询
SELECT id, embedding <-> '[1,2,3]'::vector AS distance
FROM test_vectors
ORDER BY embedding <-> '[1,2,3]'::vector
LIMIT 1;
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 向量操作测试通过${NC}"
    else
        echo -e "${RED}✗ 向量操作测试失败${NC}"
        exit 1
    fi
}

# 检查 HNSW 索引
check_hnsw_index() {
    echo -e "${YELLOW}检查 HNSW 索引...${NC}"
    
    result=$(docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM pg_indexes WHERE indexname LIKE '%hnsw%' OR indexname LIKE '%embedding%';")
    
    if [ "$result" -gt 0 ]; then
        echo -e "${GREEN}✓ HNSW 索引已创建${NC}"
    else
        echo -e "${YELLOW}⚠ HNSW 索引未找到（可选）${NC}"
    fi
}

# 性能测试
performance_test() {
    echo -e "${YELLOW}运行性能测试...${NC}"
    
    # 创建性能测试表
    docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} <<EOF > /dev/null 2>&1
-- 创建性能测试表
CREATE TABLE IF NOT EXISTS perf_test (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)
);

-- 插入测试数据（如果表为空）
DO \$\$
BEGIN
    IF (SELECT COUNT(*) FROM perf_test) = 0 THEN
        INSERT INTO perf_test (embedding)
        SELECT array_agg(random()::float)::vector(1536)
        FROM generate_series(1, 1000), generate_series(1, 1536);
    END IF;
END \$\$;

-- 创建索引（如果不存在）
CREATE INDEX IF NOT EXISTS perf_test_embedding_idx 
ON perf_test USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
EOF

    # 测试查询性能
    start_time=$(date +%s%N)
    docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} -t -c "SELECT COUNT(*) FROM perf_test WHERE embedding <-> (SELECT embedding FROM perf_test LIMIT 1) < 0.5;" > /dev/null 2>&1
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))
    
    if [ $duration -lt 1000 ]; then
        echo -e "${GREEN}✓ 查询性能正常 (${duration}ms)${NC}"
    else
        echo -e "${YELLOW}⚠ 查询性能较慢 (${duration}ms)${NC}"
    fi
}

# 显示系统信息
show_system_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}系统信息${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    docker-compose exec -T postgres-pgvector psql -U ${DB_USER} -d ${DB_NAME} <<EOF
SELECT 
    version() AS postgresql_version,
    (SELECT extversion FROM pg_extension WHERE extname = 'vector') AS pgvector_version,
    current_database() AS database_name,
    current_user AS current_user;
EOF
}

# 主函数
main() {
    check_container
    check_connection
    check_pgvector
    check_vector_type
    test_vector_operations
    check_hnsw_index
    performance_test
    show_system_info
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}所有检查通过！${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# 执行主函数
main
