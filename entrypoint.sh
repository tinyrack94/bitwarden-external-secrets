#!/bin/sh

set -euo pipefail

: "${BW_HOST:?Environment variable BW_HOST is required}"
: "${BW_PASSWORD:?Environment variable BW_PASSWORD is required}"

CONFIG_DIR="$HOME/.config/Bitwarden CLI"
mkdir -p "$CONFIG_DIR"

touch "$CONFIG_DIR/data.json"
echo "{}" > "$CONFIG_DIR/data.json"

echo "🔧 Configuring Bitwarden CLI with server: $BW_HOST"
bw config server "$BW_HOST"

echo

echo "🔐 Logging in using API key..."
if ! bw login --apikey --raw > /dev/null; then
    echo "❌ Failed to log in with API key"
    exit 1
fi

echo "🔓 Unlocking vault..."
if ! export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"; then
    echo "❌ Failed to unlock vault"
    exit 1
fi

if ! bw unlock --check > /dev/null; then
    echo "❌ Unlock check failed"
    exit 1
fi

echo "✅ Bitwarden CLI is authenticated and unlocked"

echo "🚀 Starting Bitwarden CLI server on port 8087"
echo

exec "$@"
