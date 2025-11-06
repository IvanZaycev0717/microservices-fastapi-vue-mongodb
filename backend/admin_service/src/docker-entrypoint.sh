#!/bin/bash
set -e

echo "🚀 Starting Admin Service initialization..."

required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "COMMENTS_ADMIN_POSTGRES_DB_NAME")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required variable $var is not set"
        exit 1
    fi
done
echo "✅ All required environment variables are set"

echo "⏳ Waiting for database..."
DB_HOST=""
for i in {1..30}; do
    # Пробуем comments_db (Docker Compose)
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "comments_db" -U "$POSTGRES_USER" -d "$COMMENTS_ADMIN_POSTGRES_DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        DB_HOST="comments_db"
        echo "✅ Database is ready (Docker Compose)"
        break
    fi
    
    # Пробуем comments-db (Kubernetes)
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "comments-db" -U "$POSTGRES_USER" -d "$COMMENTS_ADMIN_POSTGRES_DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        DB_HOST="comments-db"
        echo "✅ Database is ready (Kubernetes)"
        break
    fi
    
    echo "📊 Waiting for database... ($i/30)"
    sleep 2
done

if [ -z "$DB_HOST" ]; then
    echo "❌ Database is still not ready after 30 attempts"
    exit 1
fi

echo "📊 Attempting database migrations..."
{
    poetry run alembic revision --autogenerate -m 'Auto migration' && \
    poetry run alembic upgrade head && \
    echo "✅ Database migrations completed successfully"
} || {
    echo "⚠️ Database migrations failed or skipped (this might be normal)"
    echo "ℹ️  Service will start anyway with existing database schema"
}

if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$COMMENTS_ADMIN_POSTGRES_DB_NAME" -c "\dt comments;" > /dev/null 2>&1; then
    echo "✅ Database table 'comments' is ready"
else
    echo "❌ CRITICAL: Table 'comments' not found - service may not work properly"
fi

echo "🎉 Admin Service initialization completed!"
echo "🏃 Starting Admin Service..."
exec "$@"