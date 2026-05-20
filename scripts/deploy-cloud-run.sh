#!/bin/bash
set -e

# Deploy the AI Conversation Bridge services to Google Cloud Run.
# Prerequisites: gcloud CLI authenticated and project configured.
#
# Usage:
#   ./scripts/deploy-cloud-run.sh [REGION]
#
# Environment variables are NOT set by this script — configure them
# in the Cloud Run console or via gcloud after deployment:
#   gcloud run services update <SERVICE> --region <REGION> --set-env-vars KEY=VALUE

REGION="${1:-us-west1}"
REPO_ROOT="$(dirname "$0")/.."

echo "=== Deploying to Cloud Run (region: $REGION) ==="
echo ""

echo "--- 1/2: mcp-demo-server ---"
gcloud run deploy mcp-demo-server \
  --source "$REPO_ROOT/mcp-demo-server" \
  --region "$REGION" \
  --allow-unauthenticated

echo ""
echo "--- 2/2: chat-connector ---"
gcloud run deploy chat-connector \
  --source "$REPO_ROOT/chat-connector" \
  --region "$REGION" \
  --allow-unauthenticated

echo ""
echo "=== Deployment Complete ==="
echo "Next steps:"
echo "  1. Set environment variables for each service:"
echo "     gcloud run services update chat-connector --region $REGION --set-env-vars KEY=VALUE"
echo "     gcloud run services update mcp-demo-server --region $REGION --set-env-vars KEY=VALUE"
echo "  2. Update your Flowise flow's MCP URL to point to the deployed mcp-demo-server."
echo "  3. Set chat platform callbacks:"
echo "     LINE WORKS: chat-connector URL + /lineworks/callback"
echo "     DingTalk:   chat-connector URL + /dingtalk/callback"
