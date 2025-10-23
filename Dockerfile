# ======= 1) Base (runtime) =======
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
  && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Seoul \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 비루트 계정 생성
ARG APP_USER=appuser
ARG APP_UID=10001
RUN useradd -m -u ${APP_UID} ${APP_USER}

WORKDIR /app

# ======= 2) Builder (deps compile) =======
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/dist -r requirements.txt

FROM runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libxml2 \
    libxslt1.1 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /dist /wheels
RUN pip install --no-cache-dir /wheels/*.whl

COPY . /app

ARG APP_USER=appuser
USER ${APP_USER}

ENV CRAWLER_PROVIDER=seibro \
    CRAWLER_FROM=2024-01-01 \
    CRAWLER_TO=2025-10-13 \
    CRAWLER_MAX_PAGE=10 \
    CRAWLER_SIZE=100 \
    LOG_LEVEL=INFO \
    PYTHONPATH=/app

CMD ["python","-m","interfaces.main"]
