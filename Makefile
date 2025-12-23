.PHONY: install test test-health test-loan test-redeem test-position test-margin test-internal test-report clean help

help:
	@echo "可用的命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make test         - 运行所有测试"
	@echo "  make test-health  - 运行健康检查测试"
	@echo "  make test-loan    - 运行借款相关测试"
	@echo "  make test-redeem  - 运行赎回相关测试"
	@echo "  make test-position - 运行仓位相关测试"
	@echo "  make test-margin   - 运行保证金相关测试"
	@echo "  make test-internal - 运行内部接口测试"
	@echo "  make test-report  - 生成 HTML 测试报告"
	@echo "  make clean        - 清理测试生成的文件"

install:
	pip3 install -r requirements.txt

test:
	pytest

test-health:
	pytest -m health

test-loan:
	pytest -m loan

test-redeem:
	pytest -m redeem

test-position:
	pytest -m position

test-margin:
	pytest -m margin

test-internal:
	pytest -m internal

test-report:
	mkdir -p reports
	pytest --html=reports/report.html --self-contained-html

clean:
	rm -rf __pycache__ .pytest_cache htmlcov .coverage reports
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

