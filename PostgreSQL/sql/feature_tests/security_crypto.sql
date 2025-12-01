-- PostgreSQL 17.x 加密功能测试
-- 版本：PostgreSQL 17+
-- 用途：测试pgcrypto扩展和加密功能
-- 执行环境：PostgreSQL 17+ 或兼容版本

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本和扩展
SELECT version();
SELECT extname, extversion FROM pg_extension WHERE extname = 'pgcrypto';

-- 1.2 创建测试环境
CREATE SCHEMA IF NOT EXISTS ft_sec_crypto;
SET search_path TO ft_sec_crypto, public;

-- =====================
-- 2. 基础加密功能测试
-- =====================

-- 2.1 哈希函数测试
SELECT 
    'Hash Functions Test' as test_type,
    md5('Hello World') as md5_hash,
    sha1('Hello World') as sha1_hash,
    sha256('Hello World') as sha256_hash,
    sha512('Hello World') as sha512_hash;

-- 2.2 密码哈希测试
SELECT 
    'Password Hashing Test' as test_type,
    crypt('mypassword', gen_salt('bf')) as bcrypt_hash,
    crypt('mypassword', gen_salt('md5')) as md5_crypt_hash,
    crypt('mypassword', gen_salt('des')) as des_crypt_hash;

-- 2.3 随机数生成测试
SELECT 
    'Random Generation Test' as test_type,
    gen_random_bytes(16) as random_bytes,
    gen_random_uuid() as random_uuid,
    gen_salt('bf') as bcrypt_salt,
    gen_salt('md5') as md5_salt;

-- =====================
-- 3. 对称加密测试
-- =====================

-- 3.1 AES加密测试
DO $$
DECLARE
    plaintext text := 'This is sensitive data that needs encryption';
    encryption_key text := 'my-secret-key-32-chars-long!!';
    encrypted_data bytea;
    decrypted_data text;
BEGIN
    -- 加密数据
    encrypted_data := encrypt(plaintext::bytea, encryption_key, 'aes');
    
    -- 解密数据
    decrypted_data := decrypt(encrypted_data, encryption_key, 'aes');
    
    -- 验证结果
    RAISE NOTICE 'Original: %', plaintext;
    RAISE NOTICE 'Encrypted: %', encode(encrypted_data, 'hex');
    RAISE NOTICE 'Decrypted: %', decrypted_data;
    RAISE NOTICE 'Match: %', (plaintext = decrypted_data);
END $$;

-- 3.2 3DES加密测试
DO $$
DECLARE
    plaintext text := 'Another sensitive message';
    encryption_key text := '24-character-key-here!!';
    encrypted_data bytea;
    decrypted_data text;
BEGIN
    -- 加密数据
    encrypted_data := encrypt(plaintext::bytea, encryption_key, '3des');
    
    -- 解密数据
    decrypted_data := decrypt(encrypted_data, encryption_key, '3des');
    
    -- 验证结果
    RAISE NOTICE '3DES Original: %', plaintext;
    RAISE NOTICE '3DES Encrypted: %', encode(encrypted_data, 'hex');
    RAISE NOTICE '3DES Decrypted: %', decrypted_data;
    RAISE NOTICE '3DES Match: %', (plaintext = decrypted_data);
END $$;

-- =====================
-- 4. 非对称加密测试
-- =====================

-- 4.1 RSA密钥生成和加密测试
DO $$
DECLARE
    public_key text;
    private_key text;
    plaintext text := 'RSA encrypted message';
    encrypted_data bytea;
    decrypted_data text;
BEGIN
    -- 生成RSA密钥对
    SELECT public_key, private_key INTO public_key, private_key
    FROM generate_rsa_keypair(2048);
    
    -- 使用公钥加密
    encrypted_data := pgp_pub_encrypt(plaintext, public_key);
    
    -- 使用私钥解密
    decrypted_data := pgp_pub_decrypt(encrypted_data, private_key);
    
    -- 验证结果
    RAISE NOTICE 'RSA Original: %', plaintext;
    RAISE NOTICE 'RSA Encrypted: %', encode(encrypted_data, 'hex');
    RAISE NOTICE 'RSA Decrypted: %', decrypted_data;
    RAISE NOTICE 'RSA Match: %', (plaintext = decrypted_data);
END $$;

-- =====================
-- 5. 数字签名测试
-- =====================

-- 5.1 数字签名生成和验证
DO $$
DECLARE
    public_key text;
    private_key text;
    message text := 'This message needs to be signed';
    signature bytea;
    is_valid boolean;
BEGIN
    -- 生成密钥对
    SELECT public_key, private_key INTO public_key, private_key
    FROM generate_rsa_keypair(2048);
    
    -- 生成数字签名
    signature := pgp_pub_sign(message, private_key);
    
    -- 验证数字签名
    is_valid := pgp_pub_verify(message, signature, public_key);
    
    -- 验证结果
    RAISE NOTICE 'Message: %', message;
    RAISE NOTICE 'Signature: %', encode(signature, 'hex');
    RAISE NOTICE 'Signature Valid: %', is_valid;
END $$;

-- =====================
-- 6. 加密表设计
-- =====================

-- 6.1 创建加密表
DROP TABLE IF EXISTS encrypted_data CASCADE;
CREATE TABLE encrypted_data (
    id bigserial PRIMARY KEY,
    user_id text NOT NULL,
    encrypted_personal_info bytea NOT NULL,
    encrypted_financial_info bytea,
    encryption_key_id text NOT NULL,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 6.2 创建加密函数
CREATE OR REPLACE FUNCTION encrypt_personal_info(
    personal_info jsonb,
    encryption_key text
) RETURNS bytea AS $$
BEGIN
    RETURN encrypt(personal_info::text::bytea, encryption_key, 'aes');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_personal_info(
    encrypted_data bytea,
    encryption_key text
) RETURNS jsonb AS $$
BEGIN
    RETURN decrypt(encrypted_data, encryption_key, 'aes')::text::jsonb;
END;
$$ LANGUAGE plpgsql;

-- 6.3 插入加密数据
INSERT INTO encrypted_data (user_id, encrypted_personal_info, encrypted_financial_info, encryption_key_id)
VALUES 
('USER001', 
 encrypt_personal_info('{"name": "John Doe", "email": "john@example.com", "phone": "+1-555-0123"}', 'key001'),
 encrypt('{"salary": 75000, "account": "****1234"}', 'key001', 'aes'),
 'key001'),
('USER002',
 encrypt_personal_info('{"name": "Jane Smith", "email": "jane@example.com", "phone": "+1-555-0456"}', 'key002'),
 encrypt('{"salary": 85000, "account": "****5678"}', 'key002', 'aes'),
 'key002');

-- 6.4 查询解密数据
SELECT 
    user_id,
    decrypt_personal_info(encrypted_personal_info, 'key001') as personal_info,
    decrypt(encrypted_financial_info, 'key001', 'aes')::text as financial_info
FROM encrypted_data
WHERE encryption_key_id = 'key001';

-- =====================
-- 7. 密钥管理
-- =====================

-- 7.1 创建密钥管理表
DROP TABLE IF EXISTS encryption_keys CASCADE;
CREATE TABLE encryption_keys (
    key_id text PRIMARY KEY,
    key_type text NOT NULL,
    key_data bytea NOT NULL,
    created_at timestamptz DEFAULT now(),
    expires_at timestamptz,
    is_active boolean DEFAULT true,
    created_by text DEFAULT current_user
);

-- 7.2 插入密钥
INSERT INTO encryption_keys (key_id, key_type, key_data, expires_at)
VALUES 
('key001', 'AES', encrypt('my-secret-key-32-chars-long!!', 'master-key', 'aes'), now() + interval '1 year'),
('key002', 'AES', encrypt('another-secret-key-32-chars!!', 'master-key', 'aes'), now() + interval '1 year');

-- 7.3 密钥轮换函数
CREATE OR REPLACE FUNCTION rotate_encryption_key(
    old_key_id text,
    new_key_id text,
    master_key text
) RETURNS void AS $$
DECLARE
    old_key_data bytea;
    new_key_data bytea;
BEGIN
    -- 获取旧密钥
    SELECT key_data INTO old_key_data
    FROM encryption_keys
    WHERE key_id = old_key_id AND is_active = true;
    
    -- 生成新密钥
    new_key_data := encrypt(gen_random_bytes(32)::text, master_key, 'aes');
    
    -- 插入新密钥
    INSERT INTO encryption_keys (key_id, key_type, key_data, expires_at)
    VALUES (new_key_id, 'AES', new_key_data, now() + interval '1 year');
    
    -- 标记旧密钥为非活跃
    UPDATE encryption_keys 
    SET is_active = false 
    WHERE key_id = old_key_id;
    
    RAISE NOTICE 'Key rotated from % to %', old_key_id, new_key_id;
END;
$$ LANGUAGE plpgsql;

-- =====================
-- 8. 数据完整性验证
-- =====================

-- 8.1 创建完整性检查表
DROP TABLE IF EXISTS data_integrity CASCADE;
CREATE TABLE data_integrity (
    id bigserial PRIMARY KEY,
    data_content text NOT NULL,
    data_hash text NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- 8.2 插入数据并计算哈希
INSERT INTO data_integrity (data_content, data_hash)
SELECT 
    'Important data ' || i,
    md5('Important data ' || i)
FROM generate_series(1, 10) AS i;

-- 8.3 验证数据完整性
SELECT 
    id,
    data_content,
    data_hash,
    md5(data_content) as calculated_hash,
    (data_hash = md5(data_content)) as integrity_check
FROM data_integrity;

-- =====================
-- 9. 性能测试
-- =====================

-- 9.1 加密性能测试
\timing on

-- 测试AES加密性能
DO $$
DECLARE
    i integer;
    start_time timestamp;
    end_time timestamp;
    test_data text := 'Performance test data for encryption';
    encryption_key text := 'performance-test-key-32-chars!!';
BEGIN
    start_time := clock_timestamp();
    
    FOR i IN 1..1000 LOOP
        PERFORM encrypt(test_data::bytea, encryption_key, 'aes');
    END LOOP;
    
    end_time := clock_timestamp();
    
    RAISE NOTICE 'AES Encryption: 1000 operations in %', end_time - start_time;
END $$;

-- 测试哈希性能
DO $$
DECLARE
    i integer;
    start_time timestamp;
    end_time timestamp;
    test_data text := 'Performance test data for hashing';
BEGIN
    start_time := clock_timestamp();
    
    FOR i IN 1..10000 LOOP
        PERFORM md5(test_data);
    END LOOP;
    
    end_time := clock_timestamp();
    
    RAISE NOTICE 'MD5 Hashing: 10000 operations in %', end_time - start_time;
END $$;

\timing off

-- =====================
-- 10. 安全最佳实践
-- =====================

-- 10.1 密码策略检查
CREATE OR REPLACE FUNCTION validate_password_strength(password text)
RETURNS boolean AS $$
BEGIN
    -- 检查密码长度
    IF length(password) < 8 THEN
        RETURN false;
    END IF;
    
    -- 检查是否包含数字
    IF NOT password ~ '[0-9]' THEN
        RETURN false;
    END IF;
    
    -- 检查是否包含大写字母
    IF NOT password ~ '[A-Z]' THEN
        RETURN false;
    END IF;
    
    -- 检查是否包含小写字母
    IF NOT password ~ '[a-z]' THEN
        RETURN false;
    END IF;
    
    -- 检查是否包含特殊字符
    IF NOT password ~ '[^A-Za-z0-9]' THEN
        RETURN false;
    END IF;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- 10.2 测试密码强度
SELECT 
    'Password Strength Test' as test_type,
    validate_password_strength('weak') as weak_password,
    validate_password_strength('Strong123!') as strong_password,
    validate_password_strength('VeryStrong123!@#') as very_strong_password;

-- =====================
-- 11. 清理和总结
-- =====================

-- 11.1 显示加密测试摘要
SELECT 
    'Security Crypto Test Summary' AS test_name,
    count(*) AS total_encrypted_records,
    count(DISTINCT encryption_key_id) AS unique_keys,
    min(created_at) AS first_encryption,
    max(created_at) AS last_encryption
FROM encrypted_data;

-- 11.2 清理测试数据
-- DROP SCHEMA IF EXISTS ft_sec_crypto CASCADE;

-- =====================
-- 12. 最佳实践建议
-- =====================

/*
加密功能最佳实践：

1. 密钥管理：
   - 使用强随机密钥生成器
   - 实施密钥轮换策略
   - 安全存储和传输密钥
   - 使用密钥管理服务（KMS）

2. 算法选择：
   - 使用AES-256进行对称加密
   - 使用RSA-2048或更高进行非对称加密
   - 使用bcrypt进行密码哈希
   - 避免使用已弃用的算法（MD5、DES等）

3. 数据保护：
   - 加密敏感数据字段
   - 实施数据脱敏策略
   - 使用传输加密（SSL/TLS）
   - 定期进行安全审计

4. 性能考虑：
   - 合理选择加密算法
   - 使用硬件加速（如果可用）
   - 缓存加密密钥
   - 监控加密操作性能

5. 合规要求：
   - 遵循FIPS 140-2标准
   - 满足GDPR、SOX等法规要求
   - 实施数据保留和删除策略
   - 维护加密审计日志

6. 安全考虑：
   - 保护加密密钥不被泄露
   - 实施访问控制
   - 定期进行安全评估
   - 建立事件响应计划
*/