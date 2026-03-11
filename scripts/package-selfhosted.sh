#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "Building OpenToad selfhosted package..."

pnpm install --frozen-lockfile

pnpm build

echo "Creating distribution package..."

DIST_NAME="opentoad-selfhosted-$(date +%Y%m%d)"

mkdir -p "$DIST_NAME"

cp -r dist "$DIST_NAME/"
cp -r openclaw/dist "$DIST_NAME/openclaw-dist/"
cp -r extensions "$DIST_NAME/"
cp -r packages "$DIST_NAME/"
cp -r ui "$DIST_NAME/"
cp docker/docker-compose.selfhosted.yml "$DIST_NAME/docker-compose.yml"
cp .env.example "$DIST_NAME/.env.example"

if [ -f "docker/Dockerfile.saaS" ]; then
    cp docker/Dockerfile.saaS "$DIST_NAME/Dockerfile"
fi

tar -czf "${DIST_NAME}.tar.gz" "$DIST_NAME"

echo "Package created: ${DIST_NAME}.tar.gz"

rm -rf "$DIST_NAME"

echo "Done!"
