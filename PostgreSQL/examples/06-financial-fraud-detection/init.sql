-- PostgreSQL 18 + pgvector 2.0 金融风控系统示例
-- 最后更新: 2025-11-11
-- 特性：图结构 + 向量特征 + 实时反欺诈

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;
-- 注意：Apache AGE需要单独安装，本示例使用标准PostgreSQL实现图查询逻辑

-- 创建账户表
CREATE TABLE accounts (
    id bigserial PRIMARY KEY,
    account_number text NOT NULL UNIQUE,
    account_type text,  -- 'individual', 'corporate'
    -- 账户特征向量（基于历史交易模式生成）
    transaction_pattern vector(256),
    -- 风险评分
    risk_score numeric(5,4) DEFAULT 0.0,
    created_at timestamptz DEFAULT now()
);

-- 创建交易表
CREATE TABLE transactions (
    id bigserial PRIMARY KEY,
    from_account_id bigint REFERENCES accounts(id),
    to_account_id bigint REFERENCES accounts(id),
    amount numeric(15,2) NOT NULL,
    transaction_type text,  -- 'transfer', 'payment', 'withdrawal'
    -- 交易特征向量
    transaction_vector vector(256),
    -- 风险标记
    is_fraud boolean DEFAULT false,
    fraud_score numeric(5,4) DEFAULT 0.0,
    created_at timestamptz DEFAULT now()
);

-- 创建账户关系表（模拟图结构）
CREATE TABLE account_relationships (
    id bigserial PRIMARY KEY,
    account_a_id bigint REFERENCES accounts(id),
    account_b_id bigint REFERENCES accounts(id),
    relationship_type text,  -- 'transfer', 'shared_device', 'same_address'
    relationship_strength numeric(5,4) DEFAULT 1.0,
    created_at timestamptz DEFAULT now(),
    UNIQUE(account_a_id, account_b_id, relationship_type)
);

-- 创建向量索引（HNSW，PostgreSQL 18 异步 I/O 提升性能 2-3 倍）⭐
CREATE INDEX idx_accounts_pattern ON accounts USING hnsw (transaction_pattern vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_transactions_vector ON transactions USING hnsw (transaction_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 创建关系索引
CREATE INDEX idx_relationships_a ON account_relationships (account_a_id);
CREATE INDEX idx_relationships_b ON account_relationships (account_b_id);
CREATE INDEX idx_relationships_both ON account_relationships (account_a_id, account_b_id);

-- 创建交易索引
CREATE INDEX idx_transactions_from ON transactions (from_account_id, created_at DESC);
CREATE INDEX idx_transactions_to ON transactions (to_account_id, created_at DESC);
CREATE INDEX idx_transactions_fraud ON transactions (is_fraud, created_at DESC) WHERE is_fraud = true;

-- 插入示例数据
INSERT INTO accounts (account_number, account_type, transaction_pattern, risk_score) VALUES
('ACC001', 'individual', '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(256), 0.1),
('ACC002', 'individual', '[0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1]'::vector(256), 0.2),
('ACC003', 'corporate', '[0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2]'::vector(256), 0.05),
('ACC004', 'individual', '[0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7]'::vector(256), 0.9);  -- 高风险账户

-- 插入示例交易
INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, transaction_vector) VALUES
(1, 2, 1000.00, 'transfer', '[0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05]'::vector(256)),
(2, 3, 5000.00, 'transfer', '[0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,0.05,0.15]'::vector(256)),
(4, 1, 50000.00, 'transfer', '[0.90,0.95,1.00,0.10,0.20,0.30,0.40,0.50,0.60,0.70]'::vector(256)),  -- 可疑交易
(4, 2, 30000.00, 'transfer', '[0.85,0.90,0.95,0.15,0.25,0.35,0.45,0.55,0.65,0.75]'::vector(256));  -- 可疑交易

-- 插入账户关系
INSERT INTO account_relationships (account_a_id, account_b_id, relationship_type, relationship_strength) VALUES
(1, 2, 'transfer', 0.8),
(2, 3, 'transfer', 0.6),
(4, 1, 'transfer', 0.3),  -- 弱关系，可疑
(4, 2, 'transfer', 0.2);  -- 弱关系，可疑

-- 注意：实际使用时，向量应该是完整的256维向量
-- 这里仅作示例，实际向量需要从交易特征提取生成

-- 反欺诈检测函数：结合向量相似度和图关系分析
CREATE OR REPLACE FUNCTION detect_fraud(
    p_transaction_id bigint,
    p_similarity_threshold numeric DEFAULT 0.3,
    p_risk_threshold numeric DEFAULT 0.7
)
RETURNS TABLE (
    transaction_id bigint,
    from_account_id bigint,
    to_account_id bigint,
    amount numeric,
    fraud_score numeric,
    is_fraud boolean,
    risk_factors text[]
) AS $$
DECLARE
    v_transaction transactions%ROWTYPE;
    v_from_account accounts%ROWTYPE;
    v_to_account accounts%ROWTYPE;
    v_similar_fraud_count int;
    v_relationship_strength numeric;
    v_final_score numeric;
    v_factors text[];
BEGIN
    -- 获取交易信息
    SELECT * INTO v_transaction
    FROM transactions
    WHERE id = p_transaction_id;
    
    -- 获取账户信息
    SELECT * INTO v_from_account FROM accounts WHERE id = v_transaction.from_account_id;
    SELECT * INTO v_to_account FROM accounts WHERE id = v_transaction.to_account_id;
    
    -- 因子1：向量相似度检测（查找相似的可疑交易）
    SELECT COUNT(*) INTO v_similar_fraud_count
    FROM transactions
    WHERE is_fraud = true
      AND transaction_vector <=> v_transaction.transaction_vector < p_similarity_threshold
      AND id != p_transaction_id;
    
    -- 因子2：账户风险评分
    -- 因子3：账户关系强度（弱关系更可疑）
    SELECT COALESCE(relationship_strength, 0) INTO v_relationship_strength
    FROM account_relationships
    WHERE account_a_id = v_transaction.from_account_id
      AND account_b_id = v_transaction.to_account_id
    LIMIT 1;
    
    -- 因子4：交易金额异常
    -- 因子5：交易频率异常
    
    -- 计算综合欺诈分数
    v_final_score := 
        -- 相似欺诈交易数量（归一化）
        LEAST(v_similar_fraud_count::numeric / 10.0, 1.0) * 0.3 +
        -- 发送方账户风险
        v_from_account.risk_score * 0.25 +
        -- 接收方账户风险
        v_to_account.risk_score * 0.15 +
        -- 关系强度（弱关系更可疑）
        (1.0 - COALESCE(v_relationship_strength, 0.5)) * 0.2 +
        -- 金额异常（大额交易更可疑）
        LEAST(v_transaction.amount / 100000.0, 1.0) * 0.1;
    
    -- 构建风险因子列表
    v_factors := ARRAY[]::text[];
    IF v_similar_fraud_count > 0 THEN
        v_factors := array_append(v_factors, format('相似欺诈交易: %s', v_similar_fraud_count));
    END IF;
    IF v_from_account.risk_score > 0.5 THEN
        v_factors := array_append(v_factors, format('发送方高风险: %.2f', v_from_account.risk_score));
    END IF;
    IF v_to_account.risk_score > 0.5 THEN
        v_factors := array_append(v_factors, format('接收方高风险: %.2f', v_to_account.risk_score));
    END IF;
    IF COALESCE(v_relationship_strength, 0.5) < 0.3 THEN
        v_factors := array_append(v_factors, '账户关系薄弱');
    END IF;
    IF v_transaction.amount > 10000 THEN
        v_factors := array_append(v_factors, format('大额交易: %s', v_transaction.amount));
    END IF;
    
    -- 更新交易记录
    UPDATE transactions
    SET 
        fraud_score = v_final_score,
        is_fraud = (v_final_score >= p_risk_threshold)
    WHERE id = p_transaction_id;
    
    -- 返回结果
    RETURN QUERY
    SELECT 
        v_transaction.id,
        v_transaction.from_account_id,
        v_transaction.to_account_id,
        v_transaction.amount,
        v_final_score,
        (v_final_score >= p_risk_threshold),
        v_factors;
END;
$$ LANGUAGE plpgsql;

-- 批量检测函数
CREATE OR REPLACE FUNCTION batch_detect_fraud(
    p_time_window interval DEFAULT '1 hour',
    p_similarity_threshold numeric DEFAULT 0.3,
    p_risk_threshold numeric DEFAULT 0.7
)
RETURNS TABLE (
    transaction_id bigint,
    fraud_score numeric,
    is_fraud boolean
) AS $$
BEGIN
    RETURN QUERY
    WITH detected AS (
        SELECT 
            t.id,
            (detect_fraud(t.id, p_similarity_threshold, p_risk_threshold)).*
        FROM transactions t
        WHERE t.created_at >= now() - p_time_window
          AND t.is_fraud IS NULL OR t.is_fraud = false
    )
    SELECT 
        d.transaction_id,
        d.fraud_score,
        d.is_fraud
    FROM detected d
    WHERE d.is_fraud = true
    ORDER BY d.fraud_score DESC;
END;
$$ LANGUAGE plpgsql;

-- 账户风险评分更新函数
CREATE OR REPLACE FUNCTION update_account_risk_score(p_account_id bigint)
RETURNS void AS $$
DECLARE
    v_fraud_rate numeric;
    v_new_risk_score numeric;
BEGIN
    -- 计算账户的欺诈交易率
    SELECT 
        COUNT(*) FILTER (WHERE is_fraud = true)::float / 
        NULLIF(COUNT(*), 0)
    INTO v_fraud_rate
    FROM transactions
    WHERE from_account_id = p_account_id
       OR to_account_id = p_account_id;
    
    -- 更新风险评分（欺诈率越高，风险评分越高）
    v_new_risk_score := COALESCE(v_fraud_rate, 0.0);
    
    UPDATE accounts
    SET risk_score = v_new_risk_score
    WHERE id = p_account_id;
END;
$$ LANGUAGE plpgsql;
