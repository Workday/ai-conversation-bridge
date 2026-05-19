#!/bin/bash
set -e

# Local development setup — creates .env files and builds containers for
# smoke testing with Docker Compose. For cloud deployment, use deploy-cloud-run.sh.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Local Development Setup ==="
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is required but not installed."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Error: Docker Compose is required but not installed."; exit 1; }

echo "Prerequisites OK (Docker, Docker Compose)"
echo ""

# Create .env files from templates
for component in chat-connector mcp-demo-server; do
  if [ ! -f "$REPO_ROOT/$component/.env" ]; then
    cp "$REPO_ROOT/$component/.env.example" "$REPO_ROOT/$component/.env"
    echo "Created $component/.env from template"
  else
    echo "Skipped $component/.env (already exists)"
  fi
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "This is a local development environment for smoke testing container builds."
echo "End-to-end testing requires cloud deployment (see deploy-cloud-run.sh)."
echo ""
echo "Next steps:"
echo "  1. Edit chat-connector/.env with your credentials"
echo "  2. Run: docker compose up --build"
echo "  3. Verify both services start without errors"
echo ""
echo "See docs/setup-guide.md for full deployment instructions."
