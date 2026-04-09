FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml .
RUN uv pip install --system --no-cache "fastapi>=0.110.0" "uvicorn[standard]>=0.27.0" "neo4j>=5.0.0" "pydantic>=2.0.0" "pydantic-settings>=2.0.0" "httpx>=0.27.0"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
