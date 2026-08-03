.PHONY: test run clean

test:
	PYTHONPATH=. python -m pytest tests/ -v

run:
	PYTHONPATH=. python -m src.server

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .pytest_cache
