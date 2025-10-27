SELECT 'CREATE DATABASE comments_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'comments_db')\gexec