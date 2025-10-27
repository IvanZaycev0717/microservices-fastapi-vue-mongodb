#!/bin/bash

set -e

cleanup() {
    echo "🛑 Force cleanup - stopping all containers..."
    docker-compose -f docker-compose.test.yml down --remove-orphans
}

trap cleanup EXIT

echo "🧹 Stop all containers before testing"
docker-compose -f docker-compose.test.yml down

echo "🚀 Starting test environment..."
docker-compose -f docker-compose.test.yml up -d --build
sleep 25

echo "🧪 Run tests inside admin_service container"
docker-compose -f docker-compose.test.yml exec admin_service bash -c "
  cd /app && \
  poetry run python -m pytest -v
"

echo "✅ All tests completed successfully"