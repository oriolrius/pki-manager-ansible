#!/usr/bin/env bash
# Integration tests: a throwaway PKI Manager (backend + OpenBao, OIDC off, no Cosmian
# KMS), the module tests, then both roles twice on an Ubuntu container (the second run
# must report changed=0).
#
#   tests/integration/run.sh                     # PKI Manager 4.0.0 on 127.0.0.1:3000
#   PKI_IMAGE_TAG=4.0.1 PKI_PORT=47500 tests/integration/run.sh
#   KEEP=1 tests/integration/run.sh              # leave the stack and the container up
#
# OpenBao comes from the pki-manager-web release under test: its openbao/ folder holds
# the server config, the policies, the bootstrap script, the dev TLS script and the
# pinned fork image (image.env). run.sh fetches that folder from GitHub at tag
# v$PKI_IMAGE_TAG (read-only, no credentials). Before a release, test a local build:
#
#   PKI_IMAGE=pki-manager-backend:dev PKI_WEB_DIR=../pki-manager-web tests/integration/run.sh
#
#   PKI_IMAGE      backend image (default ghcr.io/oriolrius/pki-manager-web/backend:$PKI_IMAGE_TAG)
#   PKI_WEB_DIR    a pki-manager-web checkout to take openbao/ from (no download)
#   PKI_WEB_REF    the git ref to download instead of v$PKI_IMAGE_TAG
#   OPENBAO_IMAGE  the OpenBao image (default: image.env of that release)
#
# Needs: docker (compose v2), git, ansible-core >= 2.15, community.crypto and
# community.docker, openssl and ssh-keygen on the controller.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
export PKI_IMAGE_TAG="${PKI_IMAGE_TAG:-4.0.0}"
export PKI_IMAGE="${PKI_IMAGE:-ghcr.io/oriolrius/pki-manager-web/backend:${PKI_IMAGE_TAG}}"
export PKI_PORT="${PKI_PORT:-3000}"
export PKI_BASE_URL="http://127.0.0.1:${PKI_PORT}"
export PKI_API_URL="${PKI_BASE_URL}/api/v1"
PKI_IT_WORK="$(mktemp -d)"
export PKI_IT_WORK
export PKI_IT_UID PKI_IT_GID
PKI_IT_UID="$(id -u)"
PKI_IT_GID="$(id -g)"
export PKI_IT_OPENBAO_STATE="$PKI_IT_WORK/openbao"
TARGET="${PKI_IT_TARGET:-pki-ansible-it-target}"
compose() { docker compose -f "$HERE/compose.yml" "$@"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

cleanup() {
  if [[ "${KEEP:-}" == 1 ]]; then
    echo "KEEP=1: stack and $TARGET left running; work dir $PKI_IT_WORK"
    return
  fi
  compose --profile bootstrap down -v --remove-orphans >/dev/null 2>&1 || true
  docker rm -f "$TARGET" >/dev/null 2>&1 || true
  rm -rf "$PKI_IT_WORK"
}
trap cleanup EXIT

# PKI Manager 3.x keeps its keys in Cosmian KMS: this stack cannot run it.
if [[ "$PKI_IMAGE" == ghcr.io/oriolrius/pki-manager-web/backend:* && "${PKI_IMAGE_TAG%%.*}" =~ ^[0-3]$ ]]; then
  fail "PKI Manager $PKI_IMAGE_TAG needs Cosmian KMS; this stack runs OpenBao (PKI Manager 4.0.0+). Test 3.x with collection 3.1.0."
fi

# The openbao/ folder of the PKI Manager release under test.
if [[ -n "${PKI_WEB_DIR:-}" ]]; then
  PKI_OPENBAO_DIR="$(cd "$PKI_WEB_DIR/openbao" && pwd)"
else
  ref="${PKI_WEB_REF:-v${PKI_IMAGE_TAG}}"
  echo "== pki-manager-web openbao/ at $ref"
  git clone --quiet --depth 1 --branch "$ref" --filter=blob:none --sparse \
    https://github.com/oriolrius/pki-manager-web.git "$PKI_IT_WORK/pki-manager-web"
  git -C "$PKI_IT_WORK/pki-manager-web" sparse-checkout set openbao
  PKI_OPENBAO_DIR="$PKI_IT_WORK/pki-manager-web/openbao"
fi
export PKI_OPENBAO_DIR
for f in config/openbao.hcl scripts/bootstrap.sh scripts/dev-tls.sh image.env \
         policies/pki-manager-backend.hcl policies/pki-manager-ra.hcl; do
  [[ -f "$PKI_OPENBAO_DIR/$f" ]] || fail "$PKI_OPENBAO_DIR/$f is missing (not a PKI Manager 4 release?)"
done

# The pinned OpenBao fork image: the published image of image.env, else its local tag
# (pki-manager-web scripts/openbao-image.sh builds it). image.env is read, not sourced.
image_env() { sed -n "s/^$1=//p" "$PKI_OPENBAO_DIR/image.env" | tail -n 1; }
if [[ -z "${OPENBAO_IMAGE:-}" ]]; then
  OPENBAO_IMAGE="$(image_env OPENBAO_PUBLISHED_IMAGE)"
  if [[ -z "$OPENBAO_IMAGE" ]]; then
    OPENBAO_IMAGE="$(image_env OPENBAO_LOCAL_IMAGE)"
    docker image inspect "$OPENBAO_IMAGE" >/dev/null 2>&1 \
      || fail "no published OpenBao image in image.env, and no local image '$OPENBAO_IMAGE': build it with pki-manager-web scripts/openbao-image.sh, or set OPENBAO_IMAGE"
  fi
fi
export OPENBAO_IMAGE

# The stack must not start a Cosmian KMS, and the backend must not get its URL.
if compose --profile bootstrap config --images | grep -qi cosmian \
  || compose --profile bootstrap config | grep -q 'KMS_URL'; then
  fail "the integration stack references Cosmian KMS"
fi

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

echo "== OpenBao $OPENBAO_IMAGE"
mkdir -p "$PKI_IT_OPENBAO_STATE/secrets"
chmod 700 "$PKI_IT_OPENBAO_STATE/secrets"
bash "$PKI_OPENBAO_DIR/scripts/dev-tls.sh" "$PKI_IT_OPENBAO_STATE/tls" >/dev/null
compose up -d --quiet-pull openbao
compose --profile bootstrap run --rm --quiet-pull openbao-bootstrap dev
[[ -s "$PKI_IT_OPENBAO_STATE/secrets/backend-token" ]] || fail "the bootstrap wrote no backend token"
# The backend token is scoped: it creates, uses and deletes keys on its Transit mount.
# It cannot import keys (only the migration token can) or read the server configuration.
as_backend_out() {
  compose --profile bootstrap run --rm --entrypoint sh openbao-bootstrap -c \
    "BAO_TOKEN=\"\$(cat /openbao/secrets/backend-token)\" bao $1" 2>&1
}
as_backend() { as_backend_out "$1" >/dev/null; }
probe="it-probe-$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
{ as_backend "write -f pki-manager/keys/$probe type=ecdsa-p256" &&
  as_backend "write pki-manager/sign/$probe/sha2-256 input=aGVsbG8=" &&
  as_backend "write pki-manager/keys/$probe/config deletion_allowed=true" &&
  as_backend "delete pki-manager/keys/$probe"; } ||
  fail "the backend token cannot create, sign with and delete a key on the Transit mount pki-manager"
as_backend_out "write pki-manager/keys/$probe/import ciphertext=AAAA type=ecdsa-p256" | grep -q 'permission denied' ||
  fail "the backend token can reach the key import path (import is migration-only)"
if as_backend "read sys/mounts"; then
  fail "the backend token can read sys/mounts (not a scoped token)"
fi

echo "== PKI Manager $PKI_IMAGE on $PKI_BASE_URL"
compose up -d --quiet-pull backend
for _ in $(seq 1 90); do
  curl -fsS "$PKI_BASE_URL/health" >/dev/null 2>&1 && break
  sleep 2
done
curl -fsS "$PKI_BASE_URL/health" || { compose logs --tail 80 backend >&2; fail "the backend did not become healthy"; }
echo

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

# The keys of the run are in OpenBao Transit (dev root token: test stack only).
# shellcheck disable=SC2016  # expands in the container
keys="$(compose --profile bootstrap run --rm --entrypoint sh openbao-bootstrap -c \
  'BAO_TOKEN="$(cat /openbao/secrets/dev-root-token)" bao list -format=json pki-manager/keys' | grep -c '"' || true)"
[[ "$keys" -gt 0 ]] || fail "no key in the OpenBao Transit mount pki-manager"
echo "== OpenBao Transit mount pki-manager holds $keys keys"
echo "== All integration tests passed"
