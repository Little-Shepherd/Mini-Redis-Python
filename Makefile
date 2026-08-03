.PHONY: test run clean

test:
	PYTHONPATH=lab python -m pytest lab/ -v

verify:
	PYTHONPATH=lab python -m pytest verification/ -v

run:
	PYTHONPATH=. python -m src.server

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .pytest_cache
