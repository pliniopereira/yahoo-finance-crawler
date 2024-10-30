install:
	pip install -r requirements.txt

test:
	pytest tests/

run:
	python src/main.py --region $(region)

lint:
	flake8 --max-line-length 80 src/ tests/

fmt:
	black --line-length 80 src/ tests/

docs:
	sphinx-build -b html docs/ docs/_build/html

clean:
	find . -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "*.pyo" -exec rm -f {} +
	find . -name "*.pyd" -exec rm -f {} +
	rm -rf .mypy_cache .pytest_cache
	rm -rf docs/_build
	rm -rf build dist *.egg-info
