#!/bin/bash


echo "Stop all containers before testing"
docker-compose down

echo "Starting databases for tests..."
docker-compose up -d content_db auth_db comments_db notification_db minio
sleep 15

echo "Run FastAPI Backend"
cd src
export $(grep -v '^#' ../.env.test | xargs) && poetry run python main.py &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to start..."
for i in {1..30}; do
    curl -f http://localhost:8000/health >/dev/null 2>&1 && break
    sleep 1
done

echo "Run Pytest"
cd src
export $(grep -v '^#' ../.env.test | xargs) && poetry run python -m pytest -v
cd ..

echo "Running Postman Tests"
npx newman run "Content_Admin_API.postman_collection.json" \
  -e "Content_Admin_Devs.postman_environment.json" \
  --global-var "test_files=$PWD/postman-files" \
  --reporters="cli,htmlextra" \
  --reporter-htmlextra-export="newman_report.html" \
  --reporter-cli-no-success-assertions \
  --reporter-cli-no-console
NEWMAN_EXIT=$?

kill $BACKEND_PID
docker-compose down

if [ $NEWMAN_EXIT -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed - see newman_report.html for details"
fi

exit $NEWMAN_EXIT