import logging
from pathlib import Path

SERVICE_NAME = "CONTENT_SERVICE"

# JSON Data Paths
DATA_PATH = Path("data")

PATH_ABOUT_JSON = DATA_PATH / "about.json"


# MongoDB Database name
MONGO_DB_NAME = "content_db"

# MongoDB Connections Limits
MONGO_DB_CONNECTION_TIMEOUT_MS = 3000
MONGO_SERVER_SELECTION_TIMEOUT_MS = 3000

# Logging
LOGGING_LEVEL = logging.INFO
