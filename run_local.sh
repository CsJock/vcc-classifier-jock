#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ -f ".env.local" ]; then
  echo "Loading local env from .env.local"
  set -a
  # shellcheck disable=SC1091
  source ".env.local"
  set +a
else
  echo "Warning: .env.local not found, fallback to current shell env"
fi

HOST="${LOCAL_HOST:-127.0.0.1}"
PORT="${LOCAL_PORT:-8080}"

if command -v uv >/dev/null 2>&1; then
  exec uv run uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
fi

echo "uv not found, use python -m uvicorn fallback"
exec python3 -m uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
