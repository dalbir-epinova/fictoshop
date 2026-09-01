#!/usr/bin/env bash
set -euo pipefail

TEST_SUITE="${1:-all}"
if [[ $# -gt 0 ]]; then
  shift
fi

case "${TEST_SUITE}" in
  python|csharp|typescript|all) ;;
  *)
    echo "Usage: bash scripts/run-playwright-tests.sh [python|csharp|typescript|all] [test arguments...]" >&2
    exit 2
    ;;
esac

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_CMD="${REPO_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_CMD}" ]]; then
  echo "Python virtual environment not found: ${PYTHON_CMD}" >&2
  exit 1
fi

TEST_PORT="${FICTOSHOP_TEST_PORT:-}"
if [[ -z "${TEST_PORT}" ]]; then
  TEST_PORT="$("${PYTHON_CMD}" -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
fi

SERVER_LOG="$(mktemp -t fictoshop-playwright-server.XXXXXX)"
SERVER_PID=""

stop_server() {
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
  rm -f "${SERVER_LOG}"
}
trap stop_server EXIT INT TERM

cd "${REPO_ROOT}"
"${PYTHON_CMD}" manage.py migrate --noinput
"${PYTHON_CMD}" manage.py runserver "127.0.0.1:${TEST_PORT}" --noreload >"${SERVER_LOG}" 2>&1 &
SERVER_PID=$!
export FICTOSHOP_BASE_URL="http://127.0.0.1:${TEST_PORT}"

server_ready=false
for _ in {1..100}; do
  if "${PYTHON_CMD}" -c "import urllib.request; urllib.request.urlopen('${FICTOSHOP_BASE_URL}/meta', timeout=1)" >/dev/null 2>&1; then
    server_ready=true
    break
  fi
  if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
    break
  fi
  sleep 0.1
done

if [[ "${server_ready}" != true ]]; then
  echo "Django did not start at ${FICTOSHOP_BASE_URL}. Server output:" >&2
  sed -n '1,200p' "${SERVER_LOG}" >&2
  exit 1
fi

echo "Django test server: ${FICTOSHOP_BASE_URL}"

run_python() {
  case "${HEADED:-true}" in
    false|False|FALSE)
      "${PYTHON_CMD}" -m pytest playwright-python \
        -o "addopts=-q --browser chromium --tracing retain-on-failure --screenshot only-on-failure -p no:cacheprovider" "$@"
      ;;
    *) "${PYTHON_CMD}" -m pytest playwright-python "$@" ;;
  esac
}

run_csharp() {
  local dotnet_cmd
  if [[ -x "/opt/homebrew/opt/dotnet@8/bin/dotnet" ]]; then
    export DOTNET_ROOT="/opt/homebrew/opt/dotnet@8/libexec"
    dotnet_cmd="/opt/homebrew/opt/dotnet@8/bin/dotnet"
  else
    dotnet_cmd="$(command -v dotnet)"
  fi
  (cd "${REPO_ROOT}/playwright-csharp" && "${dotnet_cmd}" test "$@")
}

run_typescript() {
  (cd "${REPO_ROOT}/playwright-typescript" && npm test -- "$@")
}

case "${TEST_SUITE}" in
  python) run_python "$@" ;;
  csharp) run_csharp "$@" ;;
  typescript) run_typescript "$@" ;;
  all)
    run_python "$@"
    run_csharp
    run_typescript
    ;;
esac
