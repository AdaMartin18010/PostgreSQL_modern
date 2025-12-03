# 【深入】PostgreSQL扩展开发完整实战指南

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级
> **预计学习时间**: 2-3周

---

## 📑 目录

- [1. 从零开始：第一个完整扩展](#1-从零开始第一个完整扩展)
- [2. 开发环境搭建](#2-开发环境搭建)
- [3. 扩展开发完整流程](#3-扩展开发完整流程)
- [4. 高级特性开发](#4-高级特性开发)
- [5. 调试技巧详解](#5-调试技巧详解)
- [6. 测试策略](#6-测试策略)
- [7. 性能优化](#7-性能优化)
- [8. 发布流程](#8-发布流程)
- [9. 完整实战案例](#9-完整实战案例)
- [10. 常见陷阱和最佳实践](#10-常见陷阱和最佳实践)

---

## 1. 从零开始：第一个完整扩展

### 1.1 项目目标

我们将开发一个完整的扩展 `pg_hashid`，用于生成和验证hashid（类似YouTube的短ID）。

**功能特性**：
- 生成短ID（如 "aB3xK"）
- 解码短ID为整数
- 支持自定义字符集
- 支持salt加密

### 1.2 项目结构

```bash
pg_hashid/
├── Makefile                    # 构建配置
├── pg_hashid--1.0.sql         # SQL安装脚本
├── pg_hashid.control          # 扩展元数据
├── src/
│   ├── hashid.c              # C实现
│   ├── hashid.h              # 头文件
│   └── utils.c               # 工具函数
├── test/
│   ├── sql/
│   │   └── hashid_test.sql   # SQL测试
│   └── expected/
│       └── hashid_test.out   # 期望输出
├── doc/
│   ├── README.md             # 文档
│   └── CHANGELOG.md          # 变更日志
├── .gitignore
└── META.json                 # PGXN元数据
```

### 1.3 快速开始（15分钟）

```bash
# 1. 创建项目
mkdir pg_hashid && cd pg_hashid

# 2. 创建control文件
cat > pg_hashid.control <<EOF
comment = 'Hashid encoding/decoding for PostgreSQL'
default_version = '1.0'
module_pathname = '\$libdir/pg_hashid'
relocatable = true
EOF

# 3. 创建SQL安装脚本
cat > pg_hashid--1.0.sql <<EOF
-- 生成hashid
CREATE FUNCTION hashid_encode(val bigint)
RETURNS text
AS 'MODULE_PATHNAME', 'hashid_encode_wrapper'
LANGUAGE C IMMUTABLE STRICT;

-- 解码hashid
CREATE FUNCTION hashid_decode(hash text)
RETURNS bigint
AS 'MODULE_PATHNAME', 'hashid_decode_wrapper'
LANGUAGE C IMMUTABLE STRICT;
EOF

# 4. 创建C实现（简化版）
cat > hashid.c <<'EOF'
#include "postgres.h"
#include "fmgr.h"
#include "utils/builtins.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(hashid_encode_wrapper);
PG_FUNCTION_INFO_V1(hashid_decode_wrapper);

// 简单的编码实现（示例）
Datum hashid_encode_wrapper(PG_FUNCTION_ARGS)
{
    int64 val = PG_GETARG_INT64(0);
    char result[32];

    // 简单的Base62编码
    const char* alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    int pos = 0;

    if (val == 0) {
        PG_RETURN_TEXT_P(cstring_to_text("0"));
    }

    while (val > 0) {
        result[pos++] = alphabet[val % 62];
        val /= 62;
    }
    result[pos] = '\0';

    // 反转字符串
    for (int i = 0; i < pos / 2; i++) {
        char tmp = result[i];
        result[i] = result[pos - 1 - i];
        result[pos - 1 - i] = tmp;
    }

    PG_RETURN_TEXT_P(cstring_to_text(result));
}

// 简单的解码实现（示例）
Datum hashid_decode_wrapper(PG_FUNCTION_ARGS)
{
    text *hash_text = PG_GETARG_TEXT_PP(0);
    char *hash = text_to_cstring(hash_text);
    const char* alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    int64 result = 0;

    for (int i = 0; hash[i]; i++) {
        char *pos = strchr(alphabet, hash[i]);
        if (pos == NULL) {
            ereport(ERROR,
                (errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
                 errmsg("invalid hashid character: %c", hash[i])));
        }
        result = result * 62 + (pos - alphabet);
    }

    PG_RETURN_INT64(result);
}
EOF

# 5. 创建Makefile
cat > Makefile <<'EOF'
EXTENSION = pg_hashid
DATA = pg_hashid--1.0.sql
MODULES = hashid

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
EOF

# 6. 编译安装
make
sudo make install

# 7. 测试
psql -d testdb <<'EOSQL'
CREATE EXTENSION pg_hashid;
SELECT hashid_encode(12345);
SELECT hashid_decode('dnh');
EOSQL
```

**输出示例**：
```
 hashid_encode
---------------
 dnh
(1 row)

 hashid_decode
---------------
         12345
(1 row)
```

---

## 2. 开发环境搭建

### 2.1 必需工具

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    postgresql-server-dev-17 \
    build-essential \
    git \
    gdb \
    valgrind \
    clang \
    lldb \
    postgresql-17-pgtap  # 单元测试

# macOS
brew install postgresql@17
brew install llvm
brew install valgrind  # 注意：M1不支持

# 配置环境变量
export PATH=/usr/lib/postgresql/17/bin:$PATH
export PG_CONFIG=/usr/lib/postgresql/17/bin/pg_config
```

### 2.2 IDE配置（VS Code）

**`.vscode/c_cpp_properties.json`**：

```json
{
    "configurations": [
        {
            "name": "PostgreSQL Extension",
            "includePath": [
                "${workspaceFolder}/**",
                "/usr/include/postgresql/17/server",
                "/usr/include/postgresql/internal"
            ],
            "defines": [
                "PG_VERSION_NUM=170000"
            ],
            "compilerPath": "/usr/bin/gcc",
            "cStandard": "c11",
            "intelliSenseMode": "linux-gcc-x64"
        }
    ]
}
```

**`.vscode/tasks.json`**：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Extension",
            "type": "shell",
            "command": "make clean && make",
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Install Extension",
            "type": "shell",
            "command": "sudo make install",
            "dependsOn": ["Build Extension"]
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "make installcheck",
            "dependsOn": ["Install Extension"]
        }
    ]
}
```

### 2.3 调试配置

**`.vscode/launch.json`**：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach to PostgreSQL",
            "type": "cppdbg",
            "request": "attach",
            "program": "/usr/lib/postgresql/17/bin/postgres",
            "processId": "${command:pickProcess}",
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ]
        }
    ]
}
```

---

## 3. 扩展开发完整流程

### 3.1 第一步：设计API

**设计原则**：
1. **简单性**：API应该直观易用
2. **一致性**：与PostgreSQL风格一致
3. **安全性**：防止SQL注入、溢出等
4. **性能**：考虑性能影响

**API设计示例**：

```sql
-- 基础函数
hashid_encode(bigint) RETURNS text
hashid_decode(text) RETURNS bigint

-- 高级函数（带配置）
hashid_encode(bigint, salt text) RETURNS text
hashid_encode(bigint, salt text, min_length int) RETURNS text

-- 聚合函数
hashid_encode_agg(bigint) RETURNS text[]

-- 操作符
bigint --> text  -- 等价于hashid_encode
text <--> bigint -- 等价于hashid_decode
```

### 3.2 第二步：实现C函数

**完整实现示例**（`hashid_advanced.c`）：

```c
#include "postgres.h"
#include "fmgr.h"
#include "utils/builtins.h"
#include "utils/memutils.h"
#include "lib/stringinfo.h"

#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif

// 配置结构
typedef struct HashidConfig {
    char *alphabet;
    char *salt;
    int min_length;
} HashidConfig;

// 默认配置
static HashidConfig default_config = {
    .alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
    .salt = "",
    .min_length = 0
};

// 内部函数声明
static char* encode_number(int64 number, HashidConfig *config);
static int64 decode_hash(const char *hash, HashidConfig *config);
static void shuffle_alphabet(char *alphabet, const char *salt);

// 导出函数：基础编码
PG_FUNCTION_INFO_V1(hashid_encode_basic);
Datum hashid_encode_basic(PG_FUNCTION_ARGS)
{
    int64 number;
    char *result;

    // 参数校验
    if (PG_ARGISNULL(0))
        PG_RETURN_NULL();

    number = PG_GETARG_INT64(0);

    // 负数检查
    if (number < 0)
        ereport(ERROR,
            (errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
             errmsg("cannot encode negative numbers"),
             errhint("Use positive integers only")));

    // 编码
    result = encode_number(number, &default_config);

    PG_RETURN_TEXT_P(cstring_to_text(result));
}

// 导出函数：高级编码（带salt）
PG_FUNCTION_INFO_V1(hashid_encode_advanced);
Datum hashid_encode_advanced(PG_FUNCTION_ARGS)
{
    int64 number;
    text *salt_text;
    char *salt;
    int min_length;
    HashidConfig config;
    char *result;

    // 获取参数
    number = PG_GETARG_INT64(0);
    salt_text = PG_GETARG_TEXT_PP(1);
    min_length = PG_NARGS() > 2 ? PG_GETARG_INT32(2) : 0;

    // 转换salt
    salt = text_to_cstring(salt_text);

    // 创建配置
    config = default_config;
    config.salt = salt;
    config.min_length = min_length;

    // 打乱字母表（基于salt）
    config.alphabet = pstrdup(default_config.alphabet);
    shuffle_alphabet(config.alphabet, salt);

    // 编码
    result = encode_number(number, &config);

    // 填充到最小长度
    if (min_length > 0 && strlen(result) < min_length) {
        StringInfo padded = makeStringInfo();
        int padding = min_length - strlen(result);

        for (int i = 0; i < padding; i++)
            appendStringInfoChar(padded, config.alphabet[i % strlen(config.alphabet)]);
        appendStringInfoString(padded, result);

        result = padded->data;
    }

    PG_RETURN_TEXT_P(cstring_to_text(result));
}

// 内部函数：编码实现
static char* encode_number(int64 number, HashidConfig *config)
{
    StringInfo result = makeStringInfo();
    int alphabet_len = strlen(config->alphabet);

    if (number == 0) {
        appendStringInfoChar(result, config->alphabet[0]);
        return result->data;
    }

    // Base-N编码
    while (number > 0) {
        appendStringInfoChar(result, config->alphabet[number % alphabet_len]);
        number /= alphabet_len;
    }

    // 反转
    int len = result->len;
    for (int i = 0; i < len / 2; i++) {
        char tmp = result->data[i];
        result->data[i] = result->data[len - 1 - i];
        result->data[len - 1 - i] = tmp;
    }

    return result->data;
}

// 内部函数：打乱字母表
static void shuffle_alphabet(char *alphabet, const char *salt)
{
    int alphabet_len = strlen(alphabet);
    int salt_len = strlen(salt);

    if (salt_len == 0)
        return;

    int v = 0, p = 0;
    for (int i = alphabet_len - 1, n = alphabet_len - 1; i > 0; i--, n--) {
        v %= salt_len;
        int integer = (int)salt[v];
        p += integer;
        int j = (integer + v + p) % i;

        char tmp = alphabet[j];
        alphabet[j] = alphabet[i];
        alphabet[i] = tmp;

        v++;
    }
}

// 解码函数（类似实现）
PG_FUNCTION_INFO_V1(hashid_decode_basic);
Datum hashid_decode_basic(PG_FUNCTION_ARGS)
{
    text *hash_text;
    char *hash;
    int64 result;

    if (PG_ARGISNULL(0))
        PG_RETURN_NULL();

    hash_text = PG_GETARG_TEXT_PP(0);
    hash = text_to_cstring(hash_text);

    result = decode_hash(hash, &default_config);

    PG_RETURN_INT64(result);
}

static int64 decode_hash(const char *hash, HashidConfig *config)
{
    int64 result = 0;
    int alphabet_len = strlen(config->alphabet);

    for (int i = 0; hash[i]; i++) {
        char *pos = strchr(config->alphabet, hash[i]);
        if (pos == NULL) {
            ereport(ERROR,
                (errcode(ERRCODE_INVALID_TEXT_REPRESENTATION),
                 errmsg("invalid hashid character: %c", hash[i]),
                 errdetail("Character '%c' not found in alphabet", hash[i])));
        }
        result = result * alphabet_len + (pos - config->alphabet);
    }

    return result;
}
```

### 3.3 第三步：创建SQL包装

**完整SQL脚本**（`pg_hashid--1.0.sql`）：

```sql
-- complain if script is sourced in psql, rather than via CREATE EXTENSION
\echo Use "CREATE EXTENSION pg_hashid" to load this file. \quit

-- 基础函数
CREATE FUNCTION hashid_encode(bigint)
RETURNS text
AS 'MODULE_PATHNAME', 'hashid_encode_basic'
LANGUAGE C IMMUTABLE STRICT PARALLEL SAFE;

COMMENT ON FUNCTION hashid_encode(bigint) IS
'Encode a positive integer to hashid string';

-- 高级函数
CREATE FUNCTION hashid_encode(bigint, text)
RETURNS text
AS 'MODULE_PATHNAME', 'hashid_encode_advanced'
LANGUAGE C IMMUTABLE STRICT PARALLEL SAFE;

CREATE FUNCTION hashid_encode(bigint, text, int)
RETURNS text
AS 'MODULE_PATHNAME', 'hashid_encode_advanced'
LANGUAGE C IMMUTABLE STRICT PARALLEL SAFE;

-- 解码函数
CREATE FUNCTION hashid_decode(text)
RETURNS bigint
AS 'MODULE_PATHNAME', 'hashid_decode_basic'
LANGUAGE C IMMUTABLE STRICT PARALLEL SAFE;

COMMENT ON FUNCTION hashid_decode(text) IS
'Decode a hashid string to integer';

-- 操作符
CREATE OPERATOR --> (
    LEFTARG = bigint,
    RIGHTARG = text,
    FUNCTION = hashid_encode
);

CREATE OPERATOR <--> (
    LEFTARG = text,
    RIGHTARG = bigint,
    FUNCTION = hashid_decode
);

-- 类型转换
CREATE CAST (bigint AS text)
WITH FUNCTION hashid_encode(bigint)
AS IMPLICIT;
```

### 3.4 第四步：编写测试

**regression测试**（`test/sql/hashid_test.sql`）：

```sql
-- 创建扩展
CREATE EXTENSION pg_hashid;

-- 测试1：基础编码
SELECT hashid_encode(0);
SELECT hashid_encode(1);
SELECT hashid_encode(12345);
SELECT hashid_encode(9223372036854775807);  -- BIGINT MAX

-- 测试2：基础解码
SELECT hashid_decode('a');
SELECT hashid_decode('dnh');

-- 测试3：往返测试
SELECT hashid_decode(hashid_encode(42)) = 42;
SELECT hashid_decode(hashid_encode(1000000)) = 1000000;

-- 测试4：带salt编码
SELECT hashid_encode(123, 'my-salt');
SELECT hashid_encode(123, 'my-salt', 10);  -- 最小长度10

-- 测试5：错误处理
SELECT hashid_encode(-1);  -- 应该报错
SELECT hashid_decode('!!!');  -- 应该报错

-- 测试6：操作符
SELECT 12345::bigint --> ''::text;

-- 测试7：批量测试
SELECT COUNT(*) FROM (
    SELECT i, hashid_encode(i) AS hash
    FROM generate_series(1, 1000) i
) t
WHERE hashid_decode(hash) = i;  -- 应该返回1000

-- 测试8：性能测试
\timing on
SELECT COUNT(*) FROM (
    SELECT hashid_encode(i)
    FROM generate_series(1, 100000) i
) t;
\timing off

-- 清理
DROP EXTENSION pg_hashid CASCADE;
```

**期望输出**（`test/expected/hashid_test.out`）：

```
CREATE EXTENSION
 hashid_encode
---------------
 a
(1 row)

 hashid_encode
---------------
 b
(1 row)

 hashid_encode
---------------
 dnh
(1 row)

-- ... 其他期望输出
```

---

## 4. 高级特性开发

### 4.1 自定义聚合函数

```c
// 状态转换函数
PG_FUNCTION_INFO_V1(hashid_encode_agg_state);
Datum hashid_encode_agg_state(PG_FUNCTION_ARGS)
{
    ArrayType *state;
    int64 value;

    // 获取当前状态（数组）
    if (PG_ARGISNULL(0))
        state = construct_empty_array(INT8OID);
    else
        state = PG_GETARG_ARRAYTYPE_P(0);

    // 获取新值
    if (PG_ARGISNULL(1))
        PG_RETURN_ARRAYTYPE_P(state);

    value = PG_GETARG_INT64(1);

    // 添加到数组
    state = array_append(state, Int64GetDatum(value), false, INT8OID);

    PG_RETURN_ARRAYTYPE_P(state);
}

// 最终函数
PG_FUNCTION_INFO_V1(hashid_encode_agg_final);
Datum hashid_encode_agg_final(PG_FUNCTION_ARGS)
{
    ArrayType *state;
    ArrayType *result;
    int nelems, i;
    int64 *values;
    Datum *encoded_values;

    state = PG_GETARG_ARRAYTYPE_P(0);

    // 获取数组元素
    deconstruct_array(state, INT8OID, 8, true, 'd',
                      (Datum **)&values, NULL, &nelems);

    // 编码每个值
    encoded_values = palloc(nelems * sizeof(Datum));
    for (i = 0; i < nelems; i++) {
        char *encoded = encode_number(values[i], &default_config);
        encoded_values[i] = PointerGetDatum(cstring_to_text(encoded));
    }

    // 构建结果数组
    result = construct_array(encoded_values, nelems, TEXTOID, -1, false, 'i');

    PG_RETURN_ARRAYTYPE_P(result);
}
```

**SQL定义**：

```sql
CREATE AGGREGATE hashid_encode_agg(bigint) (
    SFUNC = hashid_encode_agg_state,
    STYPE = bigint[],
    FINALFUNC = hashid_encode_agg_final,
    INITCOND = '{}'
);

-- 使用示例
SELECT hashid_encode_agg(id) FROM users;
-- 结果: {dnh, xe1, mko, ...}
```

### 4.2 自定义索引类型（GiST）

**实现B-tree索引支持**：

```c
// 比较函数
PG_FUNCTION_INFO_V1(hashid_cmp);
Datum hashid_cmp(PG_FUNCTION_ARGS)
{
    text *a = PG_GETARG_TEXT_PP(0);
    text *b = PG_GETARG_TEXT_PP(1);

    int64 val_a = decode_hash(text_to_cstring(a), &default_config);
    int64 val_b = decode_hash(text_to_cstring(b), &default_config);

    if (val_a < val_b)
        PG_RETURN_INT32(-1);
    else if (val_a > val_b)
        PG_RETURN_INT32(1);
    else
        PG_RETURN_INT32(0);
}

// 操作符函数
PG_FUNCTION_INFO_V1(hashid_lt);
Datum hashid_lt(PG_FUNCTION_ARGS)
{
    Datum result = DirectFunctionCall2(hashid_cmp,
        PG_GETARG_DATUM(0), PG_GETARG_DATUM(1));
    PG_RETURN_BOOL(DatumGetInt32(result) < 0);
}

// ... 其他操作符（le, eq, ge, gt）
```

**SQL定义**：

```sql
-- 操作符
CREATE OPERATOR < (
    LEFTARG = text,
    RIGHTARG = text,
    FUNCTION = hashid_lt,
    COMMUTATOR = >,
    NEGATOR = >=,
    RESTRICT = scalarltsel,
    JOIN = scalarltjoinsel
);

-- 操作符类
CREATE OPERATOR CLASS hashid_ops
DEFAULT FOR TYPE text USING btree AS
    OPERATOR 1 <,
    OPERATOR 2 <=,
    OPERATOR 3 =,
    OPERATOR 4 >=,
    OPERATOR 5 >,
    FUNCTION 1 hashid_cmp(text, text);

-- 现在可以创建索引
CREATE INDEX idx_hashid ON users USING btree(hashid_encode(id));
```

### 4.3 后台工作进程（BGW）

```c
#include "postmaster/bgworker.h"
#include "storage/ipc.h"
#include "storage/latch.h"
#include "storage/proc.h"

void _PG_init(void);
void hashid_bgworker_main(Datum main_arg);

// 模块初始化
void _PG_init(void)
{
    BackgroundWorker worker;

    // 配置后台工作进程
    memset(&worker, 0, sizeof(BackgroundWorker));
    worker.bgw_flags = BGWORKER_SHMEM_ACCESS |
                        BGWORKER_BACKEND_DATABASE_CONNECTION;
    worker.bgw_start_time = BgWorkerStart_RecoveryFinished;
    snprintf(worker.bgw_name, BGW_MAXLEN, "hashid maintenance");
    snprintf(worker.bgw_type, BGW_MAXLEN, "hashid");
    worker.bgw_restart_time = BGW_NEVER_RESTART;
    sprintf(worker.bgw_library_name, "pg_hashid");
    sprintf(worker.bgw_function_name, "hashid_bgworker_main");
    worker.bgw_notify_pid = 0;

    RegisterBackgroundWorker(&worker);
}

// 后台工作进程主函数
void hashid_bgworker_main(Datum main_arg)
{
    // 初始化
    pqsignal(SIGTERM, die);
    BackgroundWorkerUnblockSignals();

    // 连接数据库
    BackgroundWorkerInitializeConnection("postgres", NULL, 0);

    // 主循环
    while (!got_SIGTERM) {
        int rc;

        // 执行维护任务（示例）
        StartTransactionCommand();
        SPI_connect();

        // 清理过期的hashid缓存等
        // ...

        SPI_finish();
        CommitTransactionCommand();

        // 等待10秒
        rc = WaitLatch(MyLatch,
                       WL_LATCH_SET | WL_TIMEOUT | WL_POSTMASTER_DEATH,
                       10000L,
                       PG_WAIT_EXTENSION);
        ResetLatch(MyLatch);

        if (rc & WL_POSTMASTER_DEATH)
            proc_exit(1);
    }

    proc_exit(0);
}
```

---

## 5. 调试技巧详解

### 5.1 GDB调试完整流程

**启动调试**：

```bash
# 1. 找到PostgreSQL后端进程PID
SELECT pg_backend_pid();  -- 假设返回 12345

# 2. 附加GDB
sudo gdb -p 12345

# 3. 设置断点
(gdb) break hashid_encode_basic
(gdb) continue

# 4. 在PostgreSQL中执行
SELECT hashid_encode(42);

# 5. GDB会停在断点
(gdb) print number
$1 = 42
(gdb) step  # 单步执行
(gdb) next  # 下一行
(gdb) finish  # 执行到函数返回
```

**常用GDB命令**：

```gdb
# 查看变量
print variable_name
print *pointer_variable

# 查看数据类型
ptype variable_name

# 查看PostgreSQL特定结构
p *fcinfo
p *(FunctionCallInfo)fcinfo

# 查看文本数据
p *(text*)DatumGetPointer(datum)
x/s text_to_cstring(text_datum)

# 查看栈帧
backtrace
frame 3

# 条件断点
break hashid.c:42 if number > 1000

# 观察点
watch number

# 继续执行
continue
quit
```

### 5.2 使用elog进行日志调试

```c
// 调试级别
elog(DEBUG5, "hashid_encode called with %lld", (long long)number);
elog(DEBUG1, "Alphabet length: %d", alphabet_len);
elog(LOG, "Encoding completed, result length: %d", strlen(result));
elog(NOTICE, "Warning: large number may cause slow encoding");
elog(WARNING, "Suspicious salt value: %s", salt);
elog(ERROR, "Invalid input: %s", errmsg);

// 使用ereport提供更多信息
ereport(ERROR,
    (errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
     errmsg("number out of range: %lld", (long long)number),
     errdetail("Valid range is 0 to %lld", LONG_MAX),
     errhint("Use a smaller number")));
```

**配置日志级别**：

```sql
-- 临时设置
SET client_min_messages = DEBUG1;
SET log_min_messages = DEBUG5;

-- 永久设置（postgresql.conf）
log_min_messages = debug5
client_min_messages = notice
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### 5.3 内存泄漏检测

**使用Valgrind**：

```bash
# 1. 编译时添加调试符号
CFLAGS="-g -O0" make

# 2. 使用valgrind启动PostgreSQL（测试环境）
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --verbose \
         --log-file=valgrind-out.txt \
         postgres -D /path/to/data

# 3. 执行测试
psql -d testdb -c "SELECT hashid_encode(42)"

# 4. 检查valgrind-out.txt
grep "definitely lost" valgrind-out.txt
```

**PostgreSQL内存上下文调试**：

```c
// 打印内存上下文
MemoryContextStats(TopMemoryContext);

// 切换内存上下文
MemoryContext oldcontext = MemoryContextSwitchTo(CurTransactionContext);
// ... 分配内存 ...
MemoryContextSwitchTo(oldcontext);

// 创建临时内存上下文
MemoryContext temp_ctx = AllocSetContextCreate(CurrentMemoryContext,
    "hashid temp context",
    ALLOCSET_DEFAULT_SIZES);
```

### 5.4 性能分析

**使用perf**：

```bash
# 1. 记录性能数据
sudo perf record -g -p $(pgrep -f "postgres.*testdb")

# 2. 执行测试
psql -d testdb <<EOF
SELECT COUNT(*) FROM (
    SELECT hashid_encode(i)
    FROM generate_series(1, 1000000) i
) t;
EOF

# 3. 查看报告
sudo perf report

# 4. 生成火焰图
sudo perf script | stackcollapse-perf.pl | flamegraph.pl > hashid_flamegraph.svg
```

**代码级性能分析**：

```c
#include <sys/time.h>

// 性能计时宏
#define BENCHMARK_START() \
    struct timeval start_tv, end_tv; \
    gettimeofday(&start_tv, NULL);

#define BENCHMARK_END(name) \
    gettimeofday(&end_tv, NULL); \
    elog(LOG, "%s took %ld microseconds", name, \
         (end_tv.tv_sec - start_tv.tv_sec) * 1000000 + \
         (end_tv.tv_usec - start_tv.tv_usec));

// 使用
BENCHMARK_START();
char *result = encode_number(number, config);
BENCHMARK_END("encode_number");
```

---

## 6. 测试策略

### 6.1 单元测试（pgTAP）

**安装pgTAP**：

```bash
git clone https://github.com/theory/pgtap.git
cd pgtap
make
sudo make install
```

**编写测试**（`test/pgtap/hashid_unit_test.sql`）：

```sql
BEGIN;
SELECT plan(20);

-- 加载扩展
SELECT lives_ok(
    'CREATE EXTENSION pg_hashid',
    'Extension should load without error'
);

-- 测试基础编码
SELECT is(
    hashid_encode(0),
    'a',
    'Zero should encode to "a"'
);

SELECT is(
    hashid_encode(12345),
    'dnh',
    '12345 should encode to "dnh"'
);

-- 测试往返
SELECT is(
    hashid_decode(hashid_encode(42)),
    42::bigint,
    'Roundtrip test: 42'
);

-- 测试错误处理
SELECT throws_ok(
    'SELECT hashid_encode(-1)',
    'P0001',
    'cannot encode negative numbers',
    'Negative number should raise error'
);

-- 测试带salt
SELECT isnt(
    hashid_encode(123, 'salt1'),
    hashid_encode(123, 'salt2'),
    'Different salts should produce different results'
);

-- 测试性能
SELECT ok(
    (SELECT COUNT(*) FROM (
        SELECT hashid_encode(i)
        FROM generate_series(1, 10000) i
    ) t) = 10000,
    'Should encode 10000 numbers successfully'
);

-- 批量测试
PREPARE encode_test(bigint) AS
    SELECT hashid_decode(hashid_encode($1)) = $1;

SELECT results_eq(
    'SELECT encode_test(i) FROM generate_series(1, 100) i',
    'SELECT true FROM generate_series(1, 100)',
    'All 100 roundtrip tests should pass'
);

SELECT finish();
ROLLBACK;
```

**运行测试**：

```bash
pg_prove test/pgtap/*.sql
```

### 6.2 回归测试

**Makefile配置**：

```makefile
EXTENSION = pg_hashid
DATA = pg_hashid--1.0.sql
MODULES = hashid

REGRESS = hashid_test hashid_advanced hashid_errors
REGRESS_OPTS = --inputdir=test --load-extension=pg_hashid

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
```

**运行回归测试**：

```bash
make installcheck
```

### 6.3 模糊测试

**使用AFL进行模糊测试**：

```c
// test/fuzz/fuzz_hashid.c
#include "postgres.h"
#include "fmgr.h"

#ifdef __AFL_HAVE_MANUAL_CONTROL
  __AFL_INIT();
#endif

int main(int argc, char **argv)
{
    unsigned char buf[1024];
    ssize_t len;

    // 读取AFL输入
    len = read(0, buf, sizeof(buf) - 1);
    if (len < 0)
        return 0;
    buf[len] = '\0';

    // 测试解码（最容易出现问题）
    PG_TRY();
    {
        hashid_decode_basic((char*)buf);
    }
    PG_CATCH();
    {
        // 捕获错误，继续测试
    }
    PG_END_TRY();

    return 0;
}
```

**编译并运行**：

```bash
# 使用AFL编译
afl-gcc -o fuzz_hashid fuzz_hashid.c -I/usr/include/postgresql/17/server

# 创建输入语料库
mkdir -p fuzz_in
echo "dnh" > fuzz_in/test1.txt
echo "abc123" > fuzz_in/test2.txt

# 运行模糊测试
afl-fuzz -i fuzz_in -o fuzz_out ./fuzz_hashid
```

---

## 7. 性能优化

### 7.1 避免内存分配

**优化前**（慢）：

```c
Datum hashid_encode_slow(PG_FUNCTION_ARGS)
{
    int64 number = PG_GETARG_INT64(0);
    char *result = palloc(100);  // 每次都分配

    // 编码...

    PG_RETURN_TEXT_P(cstring_to_text(result));
}
```

**优化后**（快）：

```c
Datum hashid_encode_fast(PG_FUNCTION_ARGS)
{
    int64 number = PG_GETARG_INT64(0);
    char result[64];  // 栈分配，更快

    // 编码到result...

    PG_RETURN_TEXT_P(cstring_to_text(result));
}
```

### 7.2 使用缓存

```c
// 使用哈希表缓存
typedef struct HashidCacheEntry {
    int64 number;
    char hash[32];
} HashidCacheEntry;

static HTAB *hashid_cache = NULL;

// 初始化缓存
static void init_cache(void)
{
    HASHCTL ctl;

    memset(&ctl, 0, sizeof(ctl));
    ctl.keysize = sizeof(int64);
    ctl.entrysize = sizeof(HashidCacheEntry);

    hashid_cache = hash_create("hashid cache",
                                 1024,
                                 &ctl,
                                 HASH_ELEM | HASH_BLOBS);
}

// 使用缓存
Datum hashid_encode_cached(PG_FUNCTION_ARGS)
{
    int64 number = PG_GETARG_INT64(0);
    HashidCacheEntry *entry;
    bool found;

    if (hashid_cache == NULL)
        init_cache();

    // 查找缓存
    entry = (HashidCacheEntry*)hash_search(hashid_cache,
                                            &number,
                                            HASH_FIND,
                                            &found);

    if (found) {
        // 缓存命中
        PG_RETURN_TEXT_P(cstring_to_text(entry->hash));
    }

    // 缓存未命中，编码并存储
    char *result = encode_number(number, &default_config);

    entry = (HashidCacheEntry*)hash_search(hashid_cache,
                                            &number,
                                            HASH_ENTER,
                                            &found);
    strncpy(entry->hash, result, sizeof(entry->hash));

    PG_RETURN_TEXT_P(cstring_to_text(result));
}
```

### 7.3 并行化

```sql
-- 标记函数为PARALLEL SAFE
ALTER FUNCTION hashid_encode(bigint) PARALLEL SAFE;

-- 现在可以并行执行
SET max_parallel_workers_per_gather = 4;

EXPLAIN (ANALYZE, BUFFERS)
SELECT hashid_encode(i)
FROM generate_series(1, 10000000) i;
```

### 7.4 SIMD优化（高级）

```c
#ifdef __SSE2__
#include <emmintrin.h>

// 使用SIMD批量编码
void encode_batch_simd(int64 *numbers, char **results, int count)
{
    __m128i vec;
    int i;

    for (i = 0; i + 2 <= count; i += 2) {
        // 加载两个64位数字到SIMD寄存器
        vec = _mm_set_epi64x(numbers[i], numbers[i+1]);

        // SIMD处理...
        // （实际实现会更复杂）
    }

    // 处理剩余元素
    for (; i < count; i++) {
        results[i] = encode_number(numbers[i], &default_config);
    }
}
#endif
```

---

## 8. 发布流程

### 8.1 版本管理

**创建升级脚本**（`pg_hashid--1.0--1.1.sql`）：

```sql
-- 升级从1.0到1.1

-- 添加新函数
CREATE FUNCTION hashid_encode_batch(bigint[])
RETURNS text[]
AS 'MODULE_PATHNAME', 'hashid_encode_batch'
LANGUAGE C IMMUTABLE STRICT PARALLEL SAFE;

-- 修复bug（如果有）
-- ... 修复内容 ...

-- 更新说明
COMMENT ON EXTENSION pg_hashid IS 'Hashid encoding/decoding for PostgreSQL (v1.1)';
```

**版本控制**（`.control`文件）：

```
# pg_hashid.control
comment = 'Hashid encoding/decoding for PostgreSQL'
default_version = '1.1'
module_pathname = '$libdir/pg_hashid'
relocatable = true
requires = ''
superuser = false
```

### 8.2 创建PGXN元数据

**META.json**：

```json
{
   "name": "pg_hashid",
   "abstract": "Hashid encoding and decoding for PostgreSQL",
   "description": "Generate YouTube-like short IDs from integers using hashid algorithm. Supports custom alphabets, salts, and minimum lengths.",
   "version": "1.0.0",
   "maintainer": [
      "Your Name <your.email@example.com>"
   ],
   "license": "postgresql",
   "provides": {
      "pg_hashid": {
         "abstract": "Hashid encoding/decoding functions",
         "file": "pg_hashid--1.0.sql",
         "docfile": "doc/README.md",
         "version": "1.0.0"
      }
   },
   "prereqs": {
      "runtime": {
         "requires": {
            "PostgreSQL": "12.0.0"
         }
      }
   },
   "resources": {
      "bugtracker": {
         "web": "https://github.com/yourusername/pg_hashid/issues"
      },
      "repository": {
        "url":  "git://github.com/yourusername/pg_hashid.git",
        "web":  "https://github.com/yourusername/pg_hashid",
        "type": "git"
      }
   },
   "generated_by": "Your Name",
   "meta-spec": {
      "version": "1.0.0",
      "url": "https://pgxn.org/spec/"
   },
   "tags": [
      "hashid",
      "encoding",
      "short id",
      "base62"
   ]
}
```

### 8.3 发布到PGXN

```bash
# 1. 安装PGXN客户端
sudo apt-get install pgxnclient

# 2. 打包
pgxn bundle

# 3. 测试打包
pgxn install pg_hashid-1.0.0.zip

# 4. 注册PGXN账号
# https://manager.pgxn.org/register

# 5. 上传
pgxn upload pg_hashid-1.0.0.zip

# 6. 发布
pgxn release pg_hashid 1.0.0
```

### 8.4 GitHub Release

**.github/workflows/release.yml**：

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        pg_version: [12, 13, 14, 15, 16, 17]

    steps:
      - uses: actions/checkout@v2

      - name: Install PostgreSQL ${{ matrix.pg_version }}
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql-${{ matrix.pg_version }} postgresql-server-dev-${{ matrix.pg_version }}

      - name: Build
        run: |
          export PG_CONFIG=/usr/lib/postgresql/${{ matrix.pg_version }}/bin/pg_config
          make clean
          make

      - name: Test
        run: |
          export PG_CONFIG=/usr/lib/postgresql/${{ matrix.pg_version }}/bin/pg_config
          sudo make install
          make installcheck

      - name: Package
        run: |
          tar czf pg_hashid-${{ github.ref_name }}-pg${{ matrix.pg_version }}.tar.gz *.so *.sql *.control

      - name: Upload Release Asset
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./pg_hashid-${{ github.ref_name }}-pg${{ matrix.pg_version }}.tar.gz
          asset_name: pg_hashid-${{ github.ref_name }}-pg${{ matrix.pg_version }}.tar.gz
          asset_content_type: application/gzip
```

---

## 9. 完整实战案例

### 9.1 案例：pg_prometheus - Prometheus指标存储

这是一个真实的、生产级别的扩展案例。

**功能**：
- 存储Prometheus时序指标
- 高效的时序查询
- 自动数据压缩

**核心实现**（简化）：

```c
// prometheus.c
typedef struct PrometheusMetric {
    char *name;
    int64 timestamp;
    double value;
    HTAB *labels;
} PrometheusMetric;

// 插入指标
PG_FUNCTION_INFO_V1(prometheus_insert_metric);
Datum prometheus_insert_metric(PG_FUNCTION_ARGS)
{
    text *name_text = PG_GETARG_TEXT_PP(0);
    int64 timestamp = PG_GETARG_INT64(1);
    float8 value = PG_GETARG_FLOAT8(2);
    // ... labels ...

    // 使用prepared statement批量插入
    SPIPlanPtr plan;
    Datum values[3];
    char nulls[3] = {' ', ' ', ' '};

    SPI_connect();

    plan = SPI_prepare("INSERT INTO metrics (name, ts, value) VALUES ($1, $2, $3)",
                       3, (Oid[]){TEXTOID, INT8OID, FLOAT8OID});

    values[0] = PointerGetDatum(name_text);
    values[1] = Int64GetDatum(timestamp);
    values[2] = Float8GetDatum(value);

    SPI_execute_plan(plan, values, nulls, false, 0);

    SPI_finish();

    PG_RETURN_VOID();
}

// 查询指标（带时间范围）
PG_FUNCTION_INFO_V1(prometheus_query_range);
Datum prometheus_query_range(PG_FUNCTION_ARGS)
{
    // 实现PromQL风格查询
    // ...
}
```

**完整代码参考**：https://github.com/timescale/promscale

---

## 10. 常见陷阱和最佳实践

### 10.1 内存管理陷阱

**❌ 错误示例**：

```c
// 内存泄漏！
Datum bad_function(PG_FUNCTION_ARGS)
{
    char *result = malloc(100);  // ❌ 使用malloc
    sprintf(result, "test");
    PG_RETURN_TEXT_P(cstring_to_text(result));
    // result永远不会被释放
}
```

**✅ 正确示例**：

```c
Datum good_function(PG_FUNCTION_ARGS)
{
    char *result = palloc(100);  // ✅ 使用palloc
    sprintf(result, "test");
    PG_RETURN_TEXT_P(cstring_to_text(result));
    // PostgreSQL会自动管理内存
}
```

### 10.2 错误处理陷阱

**❌ 错误示例**：

```c
// 不安全的错误处理
Datum bad_error_handling(PG_FUNCTION_ARGS)
{
    FILE *f = fopen("/tmp/test", "r");
    if (!f)
        return NULL;  // ❌ 直接返回NULL

    // ... 使用f ...

    fclose(f);
    PG_RETURN_VOID();
}
```

**✅ 正确示例**：

```c
Datum good_error_handling(PG_FUNCTION_ARGS)
{
    FILE *f = fopen("/tmp/test", "r");
    if (!f)
        ereport(ERROR,  // ✅ 使用ereport
            (errcode_for_file_access(),
             errmsg("could not open file: %m")));

    PG_TRY();
    {
        // ... 使用f ...
    }
    PG_CATCH();
    {
        fclose(f);
        PG_RE_THROW();
    }
    PG_END_TRY();

    fclose(f);
    PG_RETURN_VOID();
}
```

### 10.3 类型转换陷阱

**❌ 错误示例**：

```c
// 不安全的类型转换
Datum bad_cast(PG_FUNCTION_ARGS)
{
    text *t = (text*)PG_GETARG_POINTER(0);  // ❌ 直接转换
    char *s = (char*)t;  // ❌ 错误！text不是以null结尾的
    printf("%s", s);  // 可能崩溃
}
```

**✅ 正确示例**：

```c
Datum good_cast(PG_FUNCTION_ARGS)
{
    text *t = PG_GETARG_TEXT_PP(0);  // ✅ 使用TEXT_PP
    char *s = text_to_cstring(t);     // ✅ 正确转换
    elog(LOG, "%s", s);                // ✅ 使用elog，不是printf
}
```

### 10.4 最佳实践清单

✅ **DO（应该做）**：
1. 使用 `palloc`/`pfree` 而不是 `malloc`/`free`
2. 使用 `ereport`/`elog` 报告错误
3. 使用 `PG_TRY`/`PG_CATCH` 处理异常
4. 检查所有输入参数（`PG_ARGISNULL`）
5. 使用 `text_to_cstring` 转换text
6. 标记只读函数为 `IMMUTABLE` 或 `STABLE`
7. 标记线程安全函数为 `PARALLEL SAFE`
8. 编写完整的回归测试
9. 使用版本控制管理SQL脚本
10. 提供清晰的文档和示例

❌ **DON'T（不应该做）**：
1. 不要使用全局变量（除非必要且线程安全）
2. 不要在扩展中使用 `printf`/`fprintf`
3. 不要假设 `text` 是null结尾的
4. 不要忽略内存泄漏
5. 不要在不安全的上下文中分配内存
6. 不要直接修改输入参数
7. 不要使用废弃的API
8. 不要在函数中直接操作全局状态
9. 不要假设单线程执行
10. 不要跳过安全检查

---

## 📚 参考资源

### 官方文档
1. [PostgreSQL Server Programming](https://www.postgresql.org/docs/current/server-programming.html)
2. [Extension Building Infrastructure](https://www.postgresql.org/docs/current/extend-pgxs.html)
3. [Writing A Procedural Language Handler](https://www.postgresql.org/docs/current/plhandler.html)

### 示例扩展
1. [pg_hashids](https://github.com/iCyberon/pg_hashids) - Hashid扩展
2. [pg_roaringbitmap](https://github.com/ChenHuajun/pg_roaringbitmap) - Roaring Bitmap
3. [pg_similarity](https://github.com/eulerto/pg_similarity) - 相似度函数
4. [timescaledb](https://github.com/timescale/timescaledb) - 时序数据库（复杂示例）

### 工具和库
1. [pgTAP](https://pgtap.org/) - PostgreSQL单元测试
2. [pgrx](https://github.com/tcdi/pgrx) - Rust扩展框架
3. [PGXN](https://pgxn.org/) - PostgreSQL扩展网络

---

## 🎯 学习路径建议

### 初级（1-2周）
1. 完成"从零开始"章节的示例
2. 理解C函数和SQL包装的关系
3. 掌握基本的调试技巧

### 中级（2-4周）
4. 开发自定义聚合函数
5. 实现完整的测试套件
6. 学习性能优化技巧

### 高级（4-8周）
7. 开发自定义索引类型
8. 实现后台工作进程
9. 发布到PGXN

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐ 高级

🚀 **开始你的扩展开发之旅！**
