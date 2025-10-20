#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Defaults
# -----------------------------
IMAGE="${IMAGE:-dividend-crawler:latest}"
PROVIDER="${PROVIDER:-seibro}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
MAX_PAGE="${MAX_PAGE:-100}"
SIZE="${SIZE:-30}"
NETWORK="${NETWORK:-}"
DB_URL="${DATABASE_URL:-}"

# -----------------------------
# Helpers
# -----------------------------
usage() {
  cat <<'USAGE'
Usage: run_crawler.sh [--from-dt YYYY-MM-DD] [--to-dt YYYY-MM-DD]
                      [--provider NAME] [--max-page N] [--size N]
                      [--log-level LEVEL] [--image REPO:TAG]
                      [--db-url URL] [--network NET or '--network host']

Defaults:
  from-dt/to-dt  : 미지정 시 오늘 포함 최근 30일 (to=today, from=today-29d)
  provider       : seibro
  max-page       : 100
  size           : 30
  log-level      : INFO
  image          : dividend-crawler:latest

Examples:
  ./run_crawler.sh
  ./run_crawler.sh --from-dt 2025-10-01 --to-dt 2025-10-15
  NETWORK=appnet ./run_crawler.sh --provider seibro --log-level DEBUG
  ./run_crawler.sh --db-url 'postgresql+psycopg://user:pass@pg:5432/mydb'
USAGE
}

fmt_date() {
  local offset="$1"
  local out=""
  if TZ=Asia/Seoul date -v +0d >/dev/null 2>&1; then
    out="$(TZ=Asia/Seoul date -v ${offset}d +%F)"
  else
    if ! out="$(TZ=Asia/Seoul date -d "${offset} days" +%F 2>/dev/null)"; then
      out="$(python - <<PY
import datetime, os
KST = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(tz=KST).date()
print((today + datetime.timedelta(days=${offset})).isoformat())
PY
)"
    fi
  fi
  printf '%s' "$out"
}

# -----------------------------
# Parse args
# -----------------------------
FROM_DT=""
TO_DT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-dt) FROM_DT="${2:-}"; shift 2 ;;
    --to-dt) TO_DT="${2:-}"; shift 2 ;;
    --provider) PROVIDER="${2:-}"; shift 2 ;;
    --max-page) MAX_PAGE="${2:-}"; shift 2 ;;
    --size) SIZE="${2:-}"; shift 2 ;;
    --log-level) LOG_LEVEL="${2^^:-}"; shift 2 ;;
    --image) IMAGE="${2:-}"; shift 2 ;;
    --db-url) DB_URL="${2:-}"; shift 2 ;;
    --network) NETWORK="--network ${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

# -----------------------------
# Defaults for dates (최근 30일)
# -----------------------------
if [[ -z "${TO_DT}" ]]; then
  TO_DT="$(fmt_date 0)"
fi
if [[ -z "${FROM_DT}" ]]; then
  FROM_DT="$(fmt_date -30)"
fi

if ! [[ "$MAX_PAGE" =~ ^[0-9]+$ ]]; then
  echo "ERR: --max-page must be integer" >&2; exit 2
fi
if ! [[ "$SIZE" =~ ^[0-9]+$ ]]; then
  echo "ERR: --size must be integer" >&2; exit 2
fi

# -----------------------------
# docker run
# -----------------------------
echo "[RUN] image=${IMAGE}"
echo "[RUN] provider=${PROVIDER} from=${FROM_DT} to=${TO_DT} max-page=${MAX_PAGE} size=${SIZE} log=${LOG_LEVEL}"
if [[ -n "${DB_URL}" ]]; then
  echo "[RUN] DATABASE_URL provided"
fi
if [[ -n "${NETWORK}" ]]; then
  echo "[RUN] ${NETWORK}"
fi

docker run --rm \
  ${NETWORK} \
  -e CRAWLER_PROVIDER="${PROVIDER}" \
  -e CRAWLER_FROM="${FROM_DT}" \
  -e CRAWLER_TO="${TO_DT}" \
  -e CRAWLER_MAX_PAGE="${MAX_PAGE}" \
  -e CRAWLER_SIZE="${SIZE}" \
  -e LOG_LEVEL="${LOG_LEVEL}" \
  $( [[ -n "${DB_URL}" ]] && printf -- "-e DATABASE_URL=%s" "${DB_URL}" ) \
  "${IMAGE}"
