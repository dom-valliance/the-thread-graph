FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system -e "."

FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
