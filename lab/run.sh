#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webmin-firewalld-csrf}"
export PYTHONUNBUFFERED=1

LABEL="WEBMIN-H24-FIREWALLD-CSRF"
WITNESS="WEBMIN-H24-FIREWALLD-CSRF"
IMAGE="webmin-lab:2.670"
BASE="http://127.0.0.1:18450"
LOCK="/tmp/webmin-lab-image.lock"
PIN_TAG="2.670"
PIN_SHA="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
SRC_DEST="${PWD}/src"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  exit 1
}

clone_pin() {
  if [[ -d "${SRC_DEST}/.git" ]]; then
    local got
    got="$(git -C "${SRC_DEST}" rev-parse HEAD)"
    if [[ "${got}" == "${PIN_SHA}" ]]; then
      echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=existing-clone"
      return 0
    fi
    echo "IOC reclone tag=${PIN_TAG} got=${got} expect=${PIN_SHA}"
    rm -rf "${SRC_DEST}"
  fi
  GIT_TERMINAL_PROMPT=0 git clone --depth 1 --branch "${PIN_TAG}" \
    "${REPO_URL}" "${SRC_DEST}" || fail_setup "clone-failed"
  local got
  got="$(git -C "${SRC_DEST}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    GIT_TERMINAL_PROMPT=0 git -C "${SRC_DEST}" fetch --depth 1 origin "${PIN_SHA}" \
      || fail_setup "fetch-failed"
    git -C "${SRC_DEST}" checkout --detach "${PIN_SHA}" || fail_setup "checkout-failed"
    got="$(git -C "${SRC_DEST}" rev-parse HEAD)"
  fi
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    fail_setup "pin-mismatch got=${got}"
  fi
  echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=git-clone"
}

trap down EXIT

chmod +x poc.py firewall-cmd
mkdir -p witness
rm -f witness/firewall-cmd.log witness/default-zone
chmod 777 witness

echo "== py_compile =="
python3 -m py_compile poc.py

echo "== pin ${PIN_TAG} ${PIN_SHA} =="
clone_pin
if [[ "$(cat "${SRC_DEST}/version" 2>/dev/null || true)" != "${PIN_TAG}" ]]; then
  fail_setup "webmin-src-pin"
fi
export WEBMIN_SRC="${SRC_DEST}"
export WEBMIN_DOCKERFILE="${PWD}/Dockerfile"

echo "== shared image flock ${LOCK} ${IMAGE} =="
python3 - <<'PY'
import fcntl
import os
import subprocess
import sys

image = "webmin-lab:2.670"
lock_path = "/tmp/webmin-lab-image.lock"
src = os.environ["WEBMIN_SRC"]
dockerfile = os.environ["WEBMIN_DOCKERFILE"]
with open(lock_path, "a", encoding="utf-8") as fh:
    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if inspect.returncode == 0:
        print(f"IOC image-present {image}", flush=True)
        sys.exit(0)
    print(f"IOC image-build {image}", flush=True)
    rc = subprocess.call(["docker", "build", "-t", image, "-f", dockerfile, src])
    sys.exit(rc)
PY

down

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 8); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --no-build; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 4
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${BASE}/session_login.cgi =="
ready=0
for i in $(seq 1 60); do
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
    "${BASE}/session_login.cgi" || true)"
  if [[ "${code}" == "200" || "${code}" == "401" ]]; then
    ready=1
    echo "IOC webmin-ready attempt=${i} http=${code}"
    break
  fi
  echo "IOC webmin-wait attempt=${i} http=${code}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  fail_setup "webmin-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py
rc=$?
set -e

if [[ "${rc}" -ne 0 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
fi

if [[ ! -f poc-last-run.txt ]] || ! tail -n 1 poc-last-run.txt | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit-${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"
