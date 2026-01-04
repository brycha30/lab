mkdir -p /opt/lab/scripts

cat > /opt/lab/scripts/deploy.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

STACK="${1:-}"
if [[ -z "$STACK" ]]; then
  echo "Usage: $0 {gw|omada|stack|all}"
  exit 1
fi

REPO_ROOT="/opt/lab"
SRC_ROOT="${REPO_ROOT}/stacks"
DST_ROOT="/opt/dkr"

copy_one() {
  local s="$1"
  echo "==> Deploying stack: ${s}"
  install -d "${DST_ROOT}/${s}"
  install -m 0644 "${SRC_ROOT}/${s}/docker-compose.yml" "${DST_ROOT}/${s}/docker-compose.yml"
  echo "    Wrote: ${DST_ROOT}/${s}/docker-compose.yml"
}

case "$STACK" in
  gw|omada|stack) copy_one "$STACK" ;;
  all)
    copy_one gw
    copy_one omada
    copy_one stack
    ;;
  *)
    echo "Unknown stack: $STACK"
    echo "Usage: $0 {gw|omada|stack|all}"
    exit 2
    ;;
esac

echo "Done. (No containers restarted.)"
EOF
