#!/usr/bin/env python3
"""
修复 PostgreSQL_Formal 剩余的失效链接
"""

import re
import os
import shutil

BASE_DIR = r"e:\_src\PostgreSQL_modern\PostgreSQL_Formal"
BACKUP_DIR = os.path.join(BASE_DIR, ".link_fix_backup_2026")

def fix_file(filepath, replacements):
    """修复文件中的链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    # 修复 18.03-UUIDv7-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-NewFeatures-18", "18.03-UUIDv7-DEEP-V2.md"),
        [
            ("](#uuid_generate_v7函数)", "](#uuid_generate_v7函数)"),
            ("[范围查询性能](#范围查询性能-1)", "[范围查询性能](#范围查询性能)"),
        ]
    )
    
    # 修复 18.08-pg_upgrade-Enhancements-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-NewFeatures-18", "18.08-pg_upgrade-Enhancements-DEEP-V2.md"),
        [
            ("](#postgresql-18-新特性深度分析pg_upgrade-增强)", "](#postgresql-18-新特性深度分析pg_upgrade增强)"),
            ("](#41-pg_upgrade-cli增强)", "](#41-pg_upgradecli增强)"),
        ]
    )
    
    # 修复 18.10-CloudNativePG-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-NewFeatures-18", "18.10-CloudNativePG-DEEP-V2.md"),
        [
            ("](#总结-1)", "](#总结)"),
            ("](#参考公式汇总-1)", "](#参考公式汇总)"),
        ]
    )
    
    # 修复 18.11-OpenTelemetry-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-NewFeatures-18", "18.11-OpenTelemetry-DEEP-V2.md"),
        [
            ("](#21-pg_tracing扩展架构)", "](#21-pgtracing扩展架构)"),
        ]
    )
    
    # 修复 17.06-pg_maintain-Role-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "17-Released", "17.06-pg_maintain-Role-DEEP-V2.md"),
        [
            ("](#pg17-pg_maintain-角色与安全增强深度分析)", "](#pg17-pg_maintain角色与安全增强深度分析)"),
            ("](#12-pg_maintain-预定义角色的作用)", "](#12-pg_maintain预定义角色的作用)"),
            ("](#3-allow_alter_system-参数)", "](#3-allow_alter_system参数)"),
        ]
    )
    
    # 修复 17.07-Monitoring-Diagnostics-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "17-Released", "17.07-Monitoring-Diagnostics-DEEP-V2.md"),
        [
            ("](#2-pg_wait_events-系统视图)", "](#2-pg_wait_events系统视图)"),
            ("](#22-与-pg_stat_activity-结合使用)", "](#22-与pg_stat_activity结合使用)"),
            ("](#42-pg_stat_progress_vacuum-新字段)", "](#42-pg_stat_progress_vacuum新字段)"),
            ("](#5-pg_stat_checkpointer-视图)", "](#5-pg_stat_checkpointer视图)"),
            ("](#61-pg_stat_io-视图)", "](#61-pg_stat_io视图)"),
        ]
    )
    
    # 修复 17.08-Upgrade-Guide-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "17-Released", "17.08-Upgrade-Guide-DEEP-V2.md"),
        [
            ("](#2-pg_upgrade-升级流程)", "](#2-pg_upgrade升级流程)"),
        ]
    )
    
    # 修复 02-Storage/02.04-HeapAM-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "02-Storage", "02.04-HeapAM-DEEP-V2.md"),
        [
            ("](#52-lp_redirect机制)", "](#52-lpredirect机制)"),
        ]
    )
    
    # 修复 08-Performance/04-Memory-Benchmark-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "08-Performance", "04-Memory-Benchmark-DEEP-V2.md"),
        [
            ("](#2-shared_buffers优化)", "](#2-shared_buffers优化)"),
            ("](#3-work_mem调优)", "](#3-work_mem调优)"),
        ]
    )
    
    # 修复 09-Tools/01-vacuum-analyzer-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "09-Tools", "01-vacuum-analyzer-DEEP-V2.md"),
        [
            ("](#42-pg_visibility扩展)", "](#42-pg_visibility扩展)"),
        ]
    )
    
    # 修复 11-Database-Centric-Architecture/03-Database-Testing-Framework-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "11-Database-Centric-Architecture", "03-Database-Testing-Framework-DEEP-V2.md"),
        [
            ("](#31--fixtures模式)", "](#31-fixtures模式)"),
        ]
    )
    
    # 修复 11-Database-Centric-Architecture/11-Migration-Strategy-Guide.md
    fix_file(
        os.path.join(BASE_DIR, "11-Database-Centric-Architecture", "11-Migration-Strategy-Guide.md"),
        [
            ("](#21--strangler-fig模式-绞杀者模式)", "](#21-strangler-fig模式绞杀者模式)"),
        ]
    )
    
    # 修复 11-Database-Centric-Architecture/13-PostgreSQL18-New-Features-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "11-Database-Centric-Architecture", "13-PostgreSQL18-New-Features-DEEP-V2.md"),
        [
            ("](#102-pg_stat_io视图)", "](#102-pg_stat_io视图)"),
            ("](#11-pg_upgrade-优化统计保留)", "](#11-pg_upgrade优化统计保留)"),
        ]
    )
    
    # 修复 11-Database-Centric-Architecture/14-Distributed-Architecture-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "11-Database-Centric-Architecture", "14-Distributed-Architecture-DEEP-V2.md"),
        [
            ("](#61-postgres_fdw高级用法)", "](#61-postgres_fdw高级用法)"),
        ]
    )
    
    # 修复 11-Database-Centric-Architecture/18-Production-Deployment-Guide.md
    fix_file(
        os.path.join(BASE_DIR, "11-Database-Centric-Architecture", "18-Production-Deployment-Guide.md"),
        [
            ("](#32-pg_hbaconf配置)", "](#32-pg_hba.conf配置)"),
        ]
    )
    
    # 修复 00-Version-Specific/18-Released/18.03-UUIDv7-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "18-Released", "18.03-UUIDv7-DEEP-V2.md"),
        [
            ("](#uuid_generate_v7函数)", "](#uuid_generate_v7函数)"),
            ("](#范围查询性能-1)", "](#范围查询性能)"),
        ]
    )
    
    # 修复 00-Version-Specific/18-Released/18.08-pg_upgrade-Enhancements-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "18-Released", "18.08-pg_upgrade-Enhancements-DEEP-V2.md"),
        [
            ("](#postgresql-18-新特性深度分析pg_upgrade-增强)", "](#postgresql-18-新特性深度分析pg_upgrade增强)"),
            ("](#41-pg_upgrade-cli增强)", "](#41-pg_upgradecli增强)"),
        ]
    )
    
    # 修复 00-Version-Specific/18-Released/18.10-CloudNativePG-DEEP-V2.md
    fix_file(
        os.path.join(BASE_DIR, "00-Version-Specific", "18-Released", "18.10-CloudNativePG-DEEP-V2.md"),
        [
            ("](#总结-1)", "](#总结)"),
            ("](#参考公式汇总-1)", "](#参考公式汇总)"),
        ]
    )
    
    # 修复 LINK_VERIFICATION_SUMMARY.md
    fix_file(
        os.path.join(BASE_DIR, "LINK_VERIFICATION_SUMMARY.md"),
        [
            ("](#21-选择-selection---σ)", "](#21-选择-selection)"),
            ("](#21-选择-selection)", "](#21-选择-selection)"),
            ("](#48位时间戳--74位随机数结构)", "](#48位时间戳-74位随机数结构)"),
            ("](#数据库中心架构---持续推进路线图与行动计划-v20)", "](#数据库中心架构---持续推进路线图与行动计划-v20)"),
            ("](#️-安全监控类)", "](#安全监控类)"),
        ]
    )
    
    print("\nLink fixing completed!")

if __name__ == "__main__":
    main()
