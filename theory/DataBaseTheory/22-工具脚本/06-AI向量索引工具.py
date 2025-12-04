#!/usr/bin/env python3
"""
AI向量索引构建与管理工具
用途: 批量构建pgvector索引、监控索引健康度
创建: 2025-12-04
"""

import psycopg2
from sentence_transformers import SentenceTransformer
import argparse
from tqdm import tqdm

def build_vector_index(conn_str, table, text_column, embedding_column='embedding', 
                      batch_size=1000, model_name='all-MiniLM-L6-v2'):
    """
    批量构建向量索引
    
    Args:
        conn_str: 数据库连接字符串
        table: 表名
        text_column: 文本列名
        embedding_column: 向量列名
        batch_size: 批处理大小
        model_name: 向量模型
    """
    
    print(f"🚀 开始构建向量索引...")
    print(f"   表: {table}")
    print(f"   文本列: {text_column}")
    print(f"   模型: {model_name}")
    
    # 连接数据库
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    
    # 加载模型
    print(f"📦 加载向量模型...")
    model = SentenceTransformer(model_name)
    embedding_dim = model.get_sentence_embedding_dimension()
    
    # 确保表有embedding列
    cursor.execute(f"""
        ALTER TABLE {table} 
        ADD COLUMN IF NOT EXISTS {embedding_column} vector({embedding_dim});
    """)
    conn.commit()
    
    # 获取总行数
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {embedding_column} IS NULL")
    total_rows = cursor.fetchone()[0]
    
    print(f"📊 需要处理 {total_rows} 行")
    
    # 批量处理
    offset = 0
    with tqdm(total=total_rows, desc="生成向量") as pbar:
        while True:
            cursor.execute(f"""
                SELECT id, {text_column}
                FROM {table}
                WHERE {embedding_column} IS NULL
                ORDER BY id
                LIMIT {batch_size}
            """)
            
            batch = cursor.fetchall()
            if not batch:
                break
            
            # 生成向量
            texts = [row[1] for row in batch]
            embeddings = model.encode(texts, show_progress_bar=False)
            
            # 更新数据库
            for (id, _), emb in zip(batch, embeddings):
                cursor.execute(f"""
                    UPDATE {table}
                    SET {embedding_column} = %s
                    WHERE id = %s
                """, (emb.tolist(), id))
            
            conn.commit()
            pbar.update(len(batch))
            offset += batch_size
    
    # 创建HNSW索引
    print(f"🔨 创建HNSW索引...")
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{table}_{embedding_column}
        ON {table}
        USING hnsw ({embedding_column} vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)
    conn.commit()
    
    print(f"✅ 向量索引构建完成!")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='构建pgvector索引')
    parser.add_argument('--conn', required=True, help='数据库连接字符串')
    parser.add_argument('--table', required=True, help='表名')
    parser.add_argument('--text-column', required=True, help='文本列名')
    parser.add_argument('--batch-size', type=int, default=1000, help='批处理大小')
    
    args = parser.parse_args()
    
    build_vector_index(
        args.conn,
        args.table,
        args.text_column,
        batch_size=args.batch_size
    )
