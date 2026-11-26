#!/usr/bin/env bash
# Integration tests: a throwaway PKI Manager (backend + Cosmian KMS, OIDC off),
# the module tests, then both roles twice on an Ubuntu container (the second
# run must report changed=0).
#
#   tests/integration/run.sh                 # PKI Manager 3.19.0 on 127.0.0.1:3000
#   PKI_IMAGE_TAG=3.19.1 PKI_PORT=47500 tests/integration/run.sh
#   KEEP=1 tests/integration/run.sh          # leave the stack and the container up
#
# Needs: docker (compose v2), ansible-core >= 2.15, community.crypto and
# community.docker, openssl and ssh-keygen on the controller.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
export PKI_PORT="${PKI_PORT:-3000}"
export PKI_BASE_URL="http://127.0.0.1:${PKI_PORT}"
export PKI_API_URL="${PKI_BASE_URL}/api/v1"
PKI_IT_WORK="$(mktemp -d)"
export PKI_IT_WORK
TARGET="${PKI_IT_TARGET:-pki-ansible-it-target}"
compose() { docker compose -f "$HERE/compose.yml" "$@"; }

cleanup() {
  if [[ "${KEEP:-}" == 1 ]]; then
    echo "KEEP=1: stack and $TARGET left running; work dir $PKI_IT_WORK"
    return
  fi
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  docker rm -f "$TARGET" >/dev/null 2>&1 || true
  rm -rf "$PKI_IT_WORK"
}
trap cleanup EXIT

# The collection under test: CI checks it out at ansible_collections/oriolrius/pki_manager;
# elsewhere a symlink in the work dir gives Ansible the same layout.
if [[ "$(basename "$(dirname "$(dirname "$REPO")")")" == ansible_collections ]]; then
  COLLECTIONS="$(dirname "$(dirname "$(dirname "$REPO")")")"
else
  mkdir -p "$PKI_IT_WORK/collections/ansible_collections/oriolrius"
  ln -s "$REPO" "$PKI_IT_WORK/collections/ansible_collections/oriolrius/pki_manager"
  COLLECTIONS="$PKI_IT_WORK/collections"
fi
export ANSIBLE_COLLECTIONS_PATH="$COLLECTIONS:${ANSIBLE_COLLECTIONS_PATH:-$HOME/.ansible/collections:/usr/share/ansible/collections}"
export ANSIBLE_LOCALHOST_WARNING=False ANSIBLE_INVENTORY_UNPARSED_WARNING=False ANSIBLE_FORCE_COLOR=0

echo "== PKI Manager ${PKI_IMAGE_TAG:-3.19.0} on $PKI_BASE_URL"
compose up -d --quiet-pull
for _ in $(seq 1 90); do
  curl -fsS "$PKI_BASE_URL/health" >/dev/null 2>&1 && break
  sleep 2
done
curl -fsS "$PKI_BASE_URL/health"; echo

echo "== Test host $TARGET (Ubuntu 24.04)"
docker rm -f "$TARGET" >/dev/null 2>&1 || true
docker run -d --name "$TARGET" --hostname target.example.test ubuntu:24.04 sleep infinity >/dev/null
docker exec "$TARGET" bash -c 'apt-get -qq update >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get -qq install -y python3 openssh-server openssl ca-certificates >/dev/null && mkdir -p /run/sshd'
cat > "$PKI_IT_WORK/inventory.ini" <<EOF
[target]
$TARGET ansible_connection=community.docker.docker ansible_python_interpreter=/usr/bin/python3 ansible_become_method=su
EOF

echo "== Module tests"
ansible-playbook "$HERE/module.yml"

echo "== Role fixtures"
ansible-playbook "$HERE/setup_roles.yml"

echo "== Roles, first run"
ansible-playbook -i "$PKI_IT_WORK/inventory.ini" "$HERE/roles.yml"

echo "== Roles, second run (must change nothing)"
ansible-playbook -i "$PKI_IT_WORK/inventory.ini" "$HERE/roles.yml" | tee "$PKI_IT_WORK/second.log"
if ! grep -Eq "^${TARGET} +: ok=[0-9]+ +changed=0 " "$PKI_IT_WORK/second.log"; then
  echo "FAIL: the second run of the roles changed something" >&2
  grep -E "^changed:|^${TARGET} +:" "$PKI_IT_WORK/second.log" >&2 || true
  exit 1
fi
echo "== All integration tests passed"
