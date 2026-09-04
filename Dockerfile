FROM python:3.12-slim

ARG KTRADER_RUNTIME_UID=1000
ARG KTRADER_RUNTIME_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    KTRADER_DB_PATH=/data/ktrader.db

WORKDIR /app

RUN groupadd --gid "${KTRADER_RUNTIME_GID}" ktrader \
    && useradd --uid "${KTRADER_RUNTIME_UID}" --gid "${KTRADER_RUNTIME_GID}" --home-dir /app --shell /usr/sbin/nologin --no-create-home ktrader \
    && mkdir -p /data \
    && chown -R ktrader:ktrader /app /data

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN python -m pip install --no-cache-dir .

USER ktrader

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import json,urllib.request; p=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)); raise SystemExit(0 if p.get('data_ready') and p.get('watchdog_ok') and p.get('scanner_status') in {'READY','DEGRADED'} else 1)"

CMD ["uvicorn", "ktrader.runtime.app:app", "--host", "0.0.0.0", "--port", "8000"]
