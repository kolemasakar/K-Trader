FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    KTRADER_DB_PATH=/data/ktrader.db

WORKDIR /app

RUN groupadd --system ktrader \
    && useradd --system --gid ktrader --home-dir /app --shell /usr/sbin/nologin ktrader \
    && mkdir -p /data \
    && chown -R ktrader:ktrader /app /data

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN python -m pip install --no-cache-dir .

USER ktrader

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["uvicorn", "ktrader.runtime.app:app", "--host", "0.0.0.0", "--port", "8000"]
