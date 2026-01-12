#!/bin/bash

# llmsecurity.dev OCI Deployment Script
# Deploys static website to OCI using Docker

set -e

echo "🚀 llmsecurity.dev OCI Deployment"
echo "=================================="
echo ""

# Configuration
IMAGE_NAME="llmsecurity-web"
CONTAINER_NAME="llmsecurity-web"
PORT="8080"

# Check if we're on OCI instance or deploying remotely
if [ -f "/etc/oracle-cloud-agent/agent.yaml" ]; then
    echo "✅ Detected OCI instance - deploying locally"
    DEPLOY_MODE="local"
else
    echo "📡 Deploying to remote OCI instance"
    DEPLOY_MODE="remote"

    # Prompt for OCI instance IP/hostname
    read -p "Enter OCI instance IP or hostname: " OCI_HOST
    read -p "Enter SSH user (default: ubuntu): " SSH_USER
    SSH_USER=${SSH_USER:-ubuntu}

    echo ""
    echo "Will deploy to: ${SSH_USER}@${OCI_HOST}"
    read -p "Continue? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

echo ""
echo "🏗️  Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

echo ""
echo "🛑 Stopping existing container (if any)..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo ""
echo "🚀 Starting new container..."
docker run -d \
  --name ${CONTAINER_NAME} \
  --restart unless-stopped \
  -p ${PORT}:80 \
  ${IMAGE_NAME}:latest

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Container status:"
docker ps | grep ${CONTAINER_NAME}

echo ""
echo "🌐 Website accessible at:"
if [ "$DEPLOY_MODE" = "local" ]; then
    echo "   http://localhost:${PORT}"
else
    echo "   http://${OCI_HOST}:${PORT}"
fi

echo ""
echo "📝 Useful commands:"
echo "   View logs:    docker logs -f ${CONTAINER_NAME}"
echo "   Stop:         docker stop ${CONTAINER_NAME}"
echo "   Restart:      docker restart ${CONTAINER_NAME}"
echo "   Shell:        docker exec -it ${CONTAINER_NAME} sh"

echo ""
echo "🎉 Done!"
