install:
	poetry install

test:
	poetry run pytest tests/

run:
	poetry run python src/main.py --region $(region)

lint:
	poetry run flake8 src/ tests/

fmt:
	poetry run black src/ tests/

docs:
	poetry run sphinx-build -b html docs/ docs/_build/html

clean:
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "*.pyo" -exec rm -f {} +
	find . -name "*.pyd" -exec rm -f {} +
	rm -rf .mypy_cache .pytest_cache

	rm -rf docs/_build

	rm -rf build dist *.egg-info