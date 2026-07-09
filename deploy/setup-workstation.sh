#!/usr/bin/env bash
# setup-workstation.sh — one-time workstation provisioning
#
# Run as root on the target workstation.
# Installs the gitnexus system user, directories, systemd services, and cron.
#
# Usage:
#   sudo bash deploy/setup-workstation.sh [--token <mcp-auth-token>]
#
# After this script, developers connect with the config in:
#   docs/CURRENT/developer-mcp-setup.md

set -euo pipefail

PLATFORM_ROOT="/opt/code-repos"
GRAPH_ROOT="/opt/code-repos-graph"
GITNEXUS_HOME="/opt/gitnexus-home"
SERVICE_USER="gitnexus"
MCP_TOKEN="${1:-}"  # pass via --token or set after setup in /etc/gitnexus/mcp.env
WEB_BIND_HOST="$(hostname -I | awk '{print $1}')"
WEB_PORT="4747"

# ── Parse args ──
while [[ $# -gt 0 ]]; do
    case $1 in
        --token) MCP_TOKEN="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [[ -z "$MCP_TOKEN" ]]; then
    MCP_TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "Generated MCP auth token: $MCP_TOKEN"
    echo "(Save this — you will add it to developers' .mcp.json)"
fi

echo "=== Creating service user ==="
id "$SERVICE_USER" &>/dev/null || useradd --system --shell /bin/bash --home "$PLATFORM_ROOT" "$SERVICE_USER"

echo "=== Creating directories ==="
mkdir -p "$PLATFORM_ROOT" "$GRAPH_ROOT" "$GITNEXUS_HOME" /etc/gitnexus /var/log/platform-graph
chown -R "$SERVICE_USER:$SERVICE_USER" "$PLATFORM_ROOT" "$GRAPH_ROOT" "$GITNEXUS_HOME" /etc/gitnexus /var/log/platform-graph
chmod 750 /etc/gitnexus

echo "=== Writing MCP env file ==="
cat > /etc/gitnexus/mcp.env <<EOF
GITNEXUS_MCP_AUTH_TOKEN=${MCP_TOKEN}
EOF
chmod 640 /etc/gitnexus/mcp.env
chown root:$SERVICE_USER /etc/gitnexus/mcp.env

if [[ -z "$WEB_BIND_HOST" ]]; then
    WEB_BIND_HOST="127.0.0.1"
fi

echo "=== Writing web env file ==="
cat > /etc/gitnexus/web.env <<EOF
GITNEXUS_WEB_HOST=${WEB_BIND_HOST}
GITNEXUS_WEB_PORT=${WEB_PORT}
EOF
chmod 640 /etc/gitnexus/web.env
chown root:$SERVICE_USER /etc/gitnexus/web.env

echo "=== Installing systemd services ==="
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/gitnexus-web.service" /etc/systemd/system/
cp "$SCRIPT_DIR/gitnexus-mcp.service" /etc/systemd/system/

# Update paths in units if GRAPH_ROOT differs from /opt
if [[ "$GRAPH_ROOT" != "/opt/code-repos-graph" ]]; then
    sed -i "s|/opt/code-repos-graph|$GRAPH_ROOT|g" /etc/systemd/system/gitnexus-web.service
    sed -i "s|/opt/code-repos-graph|$GRAPH_ROOT|g" /etc/systemd/system/gitnexus-mcp.service
fi

systemctl daemon-reload
systemctl enable gitnexus-web gitnexus-mcp
systemctl start  gitnexus-web gitnexus-mcp

echo "=== Installing cron ==="
SCRIPT="${GRAPH_ROOT}/scripts/workstation-refresh.sh"
CRON_LINE="0 3 * * * PATH=/usr/local/bin:/usr/bin:/bin GRAPH_ROOT=${GRAPH_ROOT} PLATFORM_ROOT=${PLATFORM_ROOT} GITNEXUS_HOME=${GITNEXUS_HOME} ${SCRIPT} >> /var/log/platform-graph/refresh.log 2>&1"
(crontab -u "$SERVICE_USER" -l 2>/dev/null | grep -v workstation-refresh || true; echo "$CRON_LINE") | crontab -u "$SERVICE_USER" -
echo "  cron installed for user $SERVICE_USER"

echo ""
echo "=== Setup complete ==="
echo ""
echo "  Web UI:  http://${WEB_BIND_HOST}:${WEB_PORT}"
echo "  MCP URL: http://$(hostname -I | awk '{print $1}'):4748/mcp"
echo "  Token:   $MCP_TOKEN"
echo ""
echo "  systemctl status gitnexus-web"
echo "  systemctl status gitnexus-mcp"
echo ""
echo "Next: clone repos to $PLATFORM_ROOT/ as user $SERVICE_USER, then run:"
echo "  sudo -u $SERVICE_USER bash $GRAPH_ROOT/scripts/workstation-refresh.sh"
