FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY services ./services
COPY shared ./shared
COPY web ./web
RUN pip install --no-cache-dir .

RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid 10001 --home-dir /app app \
    && mkdir -p /data && chown app:app /data
USER app

ENV DATABASE_PATH=/data/platform.sqlite3
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["uvicorn", "services.platform_api:app", "--host", "0.0.0.0", "--port", "8000"]
