#!/bin/bash

echo "Run Pytest"
cd src
poetry run python -m pytest -v
cd ..

echo "Run FastAPI Backend"
cd src
poetry run python main.py &
BACKEND_PID=$!
cd ..

sleep 5

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

if [ $NEWMAN_EXIT -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed - see newman_report.html for details"
fi

exit $NEWMAN_EXIT