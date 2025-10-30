import asyncio
import sys

import grpc
from grpc_reflection.v1alpha import reflection

from logger import get_logger
from proto import comments_pb2, comments_pb2_grpc
from services.comments_service import CommentsService
from services.database import close_db, init_db
from settings import settings

logger = get_logger("main")


async def main():
    """Main application entry point for Comments gRPC service.

    Initializes database, starts gRPC server with CommentsService,
    enables reflection, and manages server lifecycle.

    Returns:
        int: Exit code (0 for success, 1 for failure).

    Note:
        - Initializes database connection before starting server
        - Registers CommentsService servicer with gRPC server
        - Enables server reflection for service discovery
        - Handles graceful shutdown on KeyboardInterrupt
        - Ensures proper cleanup of resources on exit
    """
    logger.info(f"Starting {settings.GRPC_COMMENTS_SERVICE_NAME}...")

    server = None
    try:
        await init_db()
        logger.info("Database initialized successfully")

        server = grpc.aio.server()

        comments_pb2_grpc.add_CommentsServiceServicer_to_server(
            CommentsService(), server
        )

        SERVICE_NAMES = (
            comments_pb2.DESCRIPTOR.services_by_name[
                "CommentsService"
            ].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        server_address = (
            f"{settings.GRPC_COMMENTS_HOST}:{settings.GRPC_COMMENTS_PORT}"
        )
        server.add_insecure_port(server_address)

        await server.start()
        logger.info(f"gRPC server started on {server_address}")
        logger.info("Reflection enabled")

        await server.wait_for_termination()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        return 1
    finally:
        if server:
            logger.info("Stopping gRPC server...")
            await server.stop(5)
        await close_db()
        logger.info("Application shutdown completed")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
