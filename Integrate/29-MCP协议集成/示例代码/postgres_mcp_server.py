#!/usr/bin/env python3
"""
PostgreSQL MCP Server - 生产级完整实现
技术栈: Python 3.11+, FastMCP, asyncpg
版本: 1.0.0
"""

import asyncio
import os
import json
from typing import Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from datetime import datetime

import asyncpg
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    """PostgreSQL配置"""
    database_url: str = "postgresql://postgres:password@localhost:5432/postgres"
    min_pool_size: int = 2
    max_pool_size: int = 10
    command_timeout: int = 60
    max_query_results: int = 10000
    read_only_mode: bool = True


@asynccontextmanager
async def app_lifespan(server: Server) -> AsyncIterator[dict]:
    """应用生命周期管理"""
    config = PostgresConfig(
        database_url=os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/postgres"),
        read_only_mode=os.getenv("READ_ONLY_MODE", "true").lower() == "true",
        max_query_results=int(os.getenv("MAX_QUERY_RESULTS", "10000"))
    )
    
    pool = await asyncpg.create_pool(
        config.database_url,
        min_size=config.min_pool_size,
        max_size=config.max_pool_size,
        command_timeout=config.command_timeout
    )
    
    try:
        yield {"pool": pool, "config": config}
    finally:
        await pool.close()


app = Server("postgresql-mcp-server", lifespan=app_lifespan)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri="postgres://tables",
            name="Database Tables",
            description="List of all tables in the database",
            mimeType="application/json"
        ),
        Resource(
            uri="postgres://stats",
            name="Database Statistics",
            description="Current database performance statistics",
            mimeType="application/json"
        ),
        Resource(
            uri="postgres://slow-queries",
            name="Slow Queries",
            description="Recent slow query statistics",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """读取资源"""
    ctx = app.request_context
    pool = ctx.lifespan_context["pool"]
    
    if uri == "postgres://tables":
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT schemaname, tablename, tableowner,
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 100
            """)
            return json.dumps([dict(row) for row in rows], indent=2, default=str)
    
    elif uri == "postgres://stats":
        async with pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT
                    datname,
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    round(blks_hit::numeric / nullif(blks_hit + blks_read, 0) * 100, 2) as cache_hit_ratio,
                    pg_size_pretty(pg_database_size(datname)) as db_size
                FROM pg_stat_database
                WHERE datname = current_database()
            """)
            return json.dumps(dict(stats), indent=2, default=str)
    
    elif uri == "postgres://slow-queries":
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT query, calls, mean_exec_time, rows
                FROM pg_stat_statements
                WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
                ORDER BY mean_exec_time DESC
                LIMIT 10
            """)
            return json.dumps([dict(row) for row in rows], indent=2, default=str)
    
    raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出工具"""
    return [
        Tool(
            name="execute_sql",
            description="Execute a SQL SELECT query on the PostgreSQL database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                    "params": {"type": "array", "items": {"type": "string"}, "default": []},
                    "timeout": {"type": "number", "default": 60}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="explain_query",
            description="Get execution plan for a SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to explain"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get schema information for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "schema": {"type": "string", "default": "public"}
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="analyze_table",
            description="Run ANALYZE on a table to update statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "schema": {"type": "string", "default": "public"}
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="search_tables",
            description="Search for tables and columns by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword"}
                },
                "required": ["keyword"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """调用工具"""
    ctx = app.request_context
    pool = ctx.lifespan_context["pool"]
    config = ctx.lifespan_context["config"]
    
    if name == "execute_sql":
        query = arguments.get("query", "")
        params = arguments.get("params", [])
        timeout = arguments.get("timeout", config.command_timeout)
        
        # 安全检查
        if config.read_only_mode:
            dangerous = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
            if any(query.strip().upper().startswith(d) for d in dangerous):
                return [TextContent(type="text", text="Error: Write operations not allowed in read-only mode")]
        
        try:
            async with pool.acquire() as conn:
                async with asyncio.timeout(timeout):
                    rows = await conn.fetch(query, *params)
                    result = {
                        "row_count": len(rows),
                        "columns": list(rows[0].keys()) if rows else [],
                        "data": [dict(row) for row in rows[:config.max_query_results]]
                    }
                    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "explain_query":
        query = arguments.get("query", "")
        try:
            async with pool.acquire() as conn:
                plan = await conn.fetchval(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
                return [TextContent(type="text", text=plan)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_table_schema":
        table = arguments.get("table_name")
        schema = arguments.get("schema", "public")
        try:
            async with pool.acquire() as conn:
                cols = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema=$1 AND table_name=$2
                    ORDER BY ordinal_position
                """, schema, table)
                
                indexes = await conn.fetch("""
                    SELECT indexname, indexdef FROM pg_indexes
                    WHERE schemaname=$1 AND tablename=$2
                """, schema, table)
                
                result = {
                    "columns": [dict(c) for c in cols],
                    "indexes": [dict(i) for i in indexes]
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "analyze_table":
        table = arguments.get("table_name")
        schema = arguments.get("schema", "public")
        try:
            async with pool.acquire() as conn:
                await conn.execute(f'ANALYZE "{schema}"."{table}"')
                return [TextContent(type="text", text=f"Analyzed {schema}.{table}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "search_tables":
        keyword = arguments.get("keyword", "")
        try:
            async with pool.acquire() as conn:
                pattern = f"%{keyword}%"
                rows = await conn.fetch("""
                    SELECT 'table' as type, schemaname as schema, tablename as name, NULL as column
                    FROM pg_tables WHERE tablename ILIKE $1 AND schemaname NOT IN ('pg_catalog', 'information_schema')
                    UNION ALL
                    SELECT 'column', table_schema, table_name, column_name
                    FROM information_schema.columns WHERE column_name ILIKE $1
                    AND table_schema NOT IN ('pg_catalog', 'information_schema')
                    LIMIT 20
                """, pattern)
                return [TextContent(type="text", text=json.dumps([dict(r) for r in rows], indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
