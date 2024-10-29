FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . .

RUN rm -rf /root/.cache/pypoetry

CMD ["poetry", "run", "python", "src/main.py", "--region", "Argentina"]
