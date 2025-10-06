from typing import Optional

import asyncpg
from asyncpg import Connection, Pool
from asyncpg.exceptions import (
    ConnectionDoesNotExistError,
    InvalidPasswordError,
    PostgresError,
)

from services.logger import get_logger
from settings import settings

logger = get_logger("postgres_db_connection")


class PostgresConnectionManager:
    """Manages PostgreSQL connection operations.

    Includes opening and closing connections.
    """

    def __init__(
        self, host: str, port: int, user: str, password: str, database: str
    ) -> None:
        """Initializes the PostgreSQL connection manager.

        Args:
            host: PostgreSQL host.
            port: PostgreSQL port.
            user: PostgreSQL username.
            password: PostgreSQL password.
            database: Database name.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool: Optional[Pool] = None
        self.connection: Optional[Connection] = None

    async def open_connection(self) -> Connection:
        """Establishes a connection to PostgreSQL server.

        Returns:
            Connection: Connected PostgreSQL connection instance.

        Raises:
            InvalidPasswordError: If authentication fails.
            ConnectionDoesNotExistError: If connection to server fails.
            PostgresError: For other PostgreSQL errors.
        """
        try:
            self.connection = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                timeout=settings.POSTGRES_CONNECTION_TIMEOUT,
                command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
            )

            await self.connection.execute("SELECT 1")
            logger.info("PostgreSQL connection successful")
            return self.connection

        except InvalidPasswordError as e:
            logger.exception(
                "PostgreSQL authentication failed: invalid login or password"
            )
            raise
        except ConnectionDoesNotExistError as e:
            logger.exception(f"PostgreSQL connection failed: {e}")
            raise
        except PostgresError as e:
            logger.exception(f"PostgreSQL operation failed: {e}")
            raise

    async def create_pool(self) -> Pool:
        """Creates a connection pool for PostgreSQL.

        Returns:
            Pool: PostgreSQL connection pool instance.

        Raises:
            PostgresError: If pool creation fails.
        """
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=settings.POSTGRES_POOL_MIN_SIZE,
                max_size=settings.POSTGRES_POOL_MAX_SIZE,
                timeout=settings.POSTGRES_CONNECTION_TIMEOUT,
                command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
            )

            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")

            logger.info("PostgreSQL connection pool created successfully")
            return self.pool

        except PostgresError as e:
            logger.exception(f"PostgreSQL pool creation failed: {e}")
            raise

    async def close_connection(self):
        """Closes the PostgreSQL connection if it exists."""
        if self.connection and not self.connection.is_closed():
            await self.connection.close()
            self.connection = None
            logger.info("PostgreSQL connection closed")
        else:
            logger.info("PostgreSQL was closed before")

    async def close_pool(self):
        """Closes the PostgreSQL connection pool if it exists."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL connection pool closed")


class PostgresDatabaseManager:
    """Manages PostgreSQL database operations.

    Includes existence checks and creation.
    """

    def __init__(self, connection: Connection) -> None:
        """Initializes the PostgreSQL database manager.

        Args:
            connection: Connected PostgreSQL connection instance.
        """
        self.connection = connection

    async def check_database_existence(self, db_name: str) -> bool:
        """Checks if a database exists in the PostgreSQL instance.

        Args:
            db_name: Name of the database to check.

        Returns:
            bool: True if database exists, False otherwise.
        """
        try:
            result = await self.connection.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )

            exists = result is not None
            if exists:
                logger.info(f"Database '{db_name}' exists")
            else:
                logger.warning(f"Database '{db_name}' does not exist")

            return exists

        except PostgresError as e:
            logger.exception(f"Database check failed: {e}")
            return False

    async def create_database(self, db_name: str, host: str, port: int, user: str, password: str) -> bool:
        """Creates a new database if it doesn't exist.

        Args:
            db_name: Name of the database to create.
            host: PostgreSQL host.
            port: PostgreSQL port.
            user: PostgreSQL username.
            password: PostgreSQL password.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            sys_conn = await asyncpg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database="postgres",
            )

            try:
                await sys_conn.execute(f"CREATE DATABASE {db_name}")
                logger.info(f"Database '{db_name}' created successfully")
                return True
            except asyncpg.DuplicateDatabaseError:
                logger.info(f"Database '{db_name}' already exists")
                return True
            except Exception as e:
                logger.exception(f"Failed to create database '{db_name}': {e}")
                return False
            finally:
                await sys_conn.close()

        except Exception as e:
            logger.exception(f"Failed to connect to system database: {e}")
            return False


class PostgresTableManager:
    """Manages PostgreSQL table operations.

    Includes existence checks and schema initialization.
    """

    def __init__(self, connection: Connection) -> None:
        """Initializes the PostgreSQL table manager.

        Args:
            connection: Connected PostgreSQL connection instance.
        """
        self.connection = connection

    async def table_exists(self, table_name: str) -> bool:
        """Checks if a table exists in the current database.

        Args:
            table_name: Name of the table to check.

        Returns:
            bool: True if table exists, False otherwise.
        """
        try:
            result = await self.connection.fetchval(
                """
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = $1
                """,
                table_name,
            )

            exists = result is not None
            if exists:
                logger.info(f"Table '{table_name}' exists")
            else:
                logger.warning(f"Table '{table_name}' does not exist")

            return exists

        except PostgresError as e:
            logger.exception(f"Table existence check failed: {e}")
            return False

    async def initialize_tables(self, schema_sql: str) -> bool:
        """Initializes tables using provided SQL schema.

        Args:
            schema_sql: SQL schema definition.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            await self.connection.execute(schema_sql)
            logger.info("Tables initialized successfully")
            return True

        except PostgresError as e:
            logger.exception(f"Failed to initialize tables: {e}")
            return False

    async def initialize_default_data(self, data_sql: str) -> bool:
        """Initializes default data using provided SQL.

        Args:
            data_sql: SQL for inserting default data.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            await self.connection.execute(data_sql)
            logger.info("Default data initialized successfully")
            return True

        except PostgresError as e:
            logger.exception(f"Failed to initialize default data: {e}")
            return False