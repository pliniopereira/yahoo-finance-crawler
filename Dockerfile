FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN rm -rf /root/.cache/pip

CMD ["python", "src/main.py", "--region", "Argentina"]
