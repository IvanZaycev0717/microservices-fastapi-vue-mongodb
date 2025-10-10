#!/bin/bash
set -e

echo "🚀 Starting Admin Service initialization..."

# Check environment variables
echo "🔍 Checking environment variables..."
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Database environment variables are not set"
    exit 1
fi
echo "✅ Environment variables are set"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
max_retries=30
counter=0

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "comments_db" -U "$POSTGRES_USER" -d "$COMMENTS_ADMIN_POSTGRES_DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; do
    counter=$((counter + 1))
    if [ $counter -ge $max_retries ]; then
        echo "❌ Database is not ready after $max_retries attempts"
        exit 1
    fi
    echo "📊 Waiting for database... ($counter/$max_retries)"
    sleep 2
done
echo "✅ Database is ready"

# Run database migrations
echo "📊 Running database migrations..."
if poetry run alembic revision --autogenerate -m 'Changed'; then
    echo "✅ Database migrations revision created successfully"
else
    echo "⚠️ Could not create migration revision (maybe no changes detected)"
fi

if poetry run alembic upgrade head; then
    echo "✅ Database migrations applied successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

echo "🎉 Admin Service initialization completed successfully!"

# Start application
echo "🏃 Starting Admin Service..."
exec "$@"