# PostgreSQL_Modern Makefile
# 快速执行常用任务

.PHONY: help install test clean docs docker up down backup health

# 默认目标
.DEFAULT_GOAL := help

# 配置变量
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose -f configs/docker-compose.yml
PGHOST := localhost
PGPORT := 5432
PGUSER := postgres
PGDB := mydb

# 帮助信息
help:
	@echo "PostgreSQL_Modern 快速命令"
	@echo ""
	@echo "环境管理:"
	@echo "  make install        安装Python依赖"
	@echo "  make docker-build   构建Docker镜像"
	@echo "  make up            启动Docker服务"
	@echo "  make down          停止Docker服务"
	@echo "  make logs          查看Docker日志"
	@echo ""
	@echo "测试和检查:"
	@echo "  make test          运行单元测试"
	@echo "  make lint          代码质量检查"
	@echo "  make health        健康检查"
	@echo "  make benchmark     性能基准测试"
	@echo ""
	@echo "数据库管理:"
	@echo "  make backup        备份数据库"
	@echo "  make restore       恢复数据库"
	@echo "  make vacuum        执行VACUUM"
	@echo "  make optimize      优化配置"
	@echo ""
	@echo "工具:"
	@echo "  make docs          生成文档"
	@echo "  make clean         清理临时文件"

# ============================================================
# 环境管理
# ============================================================

install:
	@echo "安装Python依赖..."
	$(PIP) install -r requirements.txt
	@echo "✓ 依赖安装完成"

docker-build:
	@echo "构建Docker镜像..."
	$(DOCKER_COMPOSE) build
	@echo "✓ 镜像构建完成"

up:
	@echo "启动Docker服务..."
	$(DOCKER_COMPOSE) up -d
	@echo "等待PostgreSQL启动..."
	@sleep 10
	@echo "✓ 服务已启动"
	@echo ""
	@echo "PostgreSQL: postgresql://$(PGUSER)@$(PGHOST):$(PGPORT)/postgres"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

down:
	@echo "停止Docker服务..."
	$(DOCKER_COMPOSE) down
	@echo "✓ 服务已停止"

logs:
	$(DOCKER_COMPOSE) logs -f postgres

# ============================================================
# 测试和检查
# ============================================================

test:
	@echo "运行单元测试..."
	$(PYTHON) -m pytest tests/ -v --cov=scripts
	@echo "✓ 测试完成"

lint:
	@echo "代码质量检查..."
	@echo "检查Python代码..."
	black --check scripts/*.py
	flake8 scripts/*.py --max-line-length=100 --ignore=E501,W503
	@echo "✓ 代码检查通过"

health:
	@echo "执行健康检查..."
	$(PYTHON) scripts/health-check-advanced.py \
		--host $(PGHOST) \
		--port $(PGPORT) \
		--dbname $(PGDB) \
		--user $(PGUSER)

benchmark:
	@echo "运行性能基准测试..."
	bash scripts/performance-benchmark.sh

# ============================================================
# 数据库管理
# ============================================================

backup:
	@echo "备份数据库..."
	@mkdir -p backups
	pg_dump -h $(PGHOST) -p $(PGPORT) -U $(PGUSER) $(PGDB) \
		| gzip > backups/$(PGDB)_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "✓ 备份完成"

restore: BACKUP_FILE ?= $(shell ls -t backups/*.sql.gz | head -1)
restore:
	@echo "恢复数据库..."
	@echo "备份文件: $(BACKUP_FILE)"
	gunzip -c $(BACKUP_FILE) | psql -h $(PGHOST) -p $(PGPORT) -U $(PGUSER) $(PGDB)
	@echo "✓ 恢复完成"

vacuum:
	@echo "执行智能VACUUM..."
	$(PYTHON) scripts/vacuum-scheduler.py \
		--host $(PGHOST) \
		--port $(PGPORT) \
		--dbname $(PGDB) \
		--user $(PGUSER) \
		--auto

optimize:
	@echo "优化PostgreSQL配置..."
	$(PYTHON) scripts/pg18-optimizer.py \
		--host $(PGHOST) \
		--port $(PGPORT) \
		--dbname $(PGDB) \
		--user $(PGUSER) \
		--apply

# ============================================================
# 工具
# ============================================================

docs:
	@echo "生成文档..."
	@echo "文档已在docs/目录下"
	@echo "打开: file://$(PWD)/README.md"

clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "benchmark_report_*.md" -delete
	find . -type f -name "*_report_*.json" -delete
	@echo "✓ 清理完成"

# ============================================================
# 开发工具
# ============================================================

shell:
	@echo "连接到PostgreSQL..."
	psql -h $(PGHOST) -p $(PGPORT) -U $(PGUSER) $(PGDB)

monitor:
	@echo "实时监控查询性能..."
	$(PYTHON) scripts/query-performance-tracker.py \
		--host $(PGHOST) \
		--port $(PGPORT) \
		--dbname $(PGDB) \
		--user $(PGUSER) \
		--monitor

index-advisor:
	@echo "运行索引顾问..."
	$(PYTHON) scripts/index-advisor.py \
		--host $(PGHOST) \
		--port $(PGPORT) \
		--dbname $(PGDB) \
		--user $(PGUSER)

# ============================================================
# CI/CD
# ============================================================

ci: lint test
	@echo "✓ CI检查通过"

cd: backup optimize health
	@echo "✓ CD部署完成"

# ============================================================
# 快速开始
# ============================================================

quick-start: install up
	@echo ""
	@echo "================================================================"
	@echo "PostgreSQL_Modern 快速开始"
	@echo "================================================================"
	@echo ""
	@echo "1. 数据库连接:"
	@echo "   make shell"
	@echo ""
	@echo "2. 健康检查:"
	@echo "   make health"
	@echo ""
	@echo "3. 性能测试:"
	@echo "   make benchmark"
	@echo ""
	@echo "4. 查看文档:"
	@echo "   cat README.md"
	@echo ""
	@echo "================================================================"
