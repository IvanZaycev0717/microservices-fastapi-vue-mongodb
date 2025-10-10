import asyncio
import sys

import grpc
from grpc_reflection.v1alpha import reflection

from services.comments_service import CommentsService
from services.database import init_db, close_db
from logger import get_logger
from settings import settings
from proto import comments_pb2_grpc, comments_pb2

logger = get_logger("main")


async def main():
    """Main application entry point."""
    logger.info(f"Starting {settings.GRPC_COMMENTS_SERVICE_NAME}...")

    server = None
    try:
        await init_db()
        logger.info("Database initialized successfully")

        # Start gRPC server
        server = grpc.aio.server()

        # Add Comments service
        comments_pb2_grpc.add_CommentsServiceServicer_to_server(
            CommentsService(), server
        )

        # Enable reflection only (без health checks)
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

        # Keep server running
        await server.wait_for_termination()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        return 1
    finally:
        # Cleanup
        if server:
            logger.info("Stopping gRPC server...")
            await server.stop(5)
        await close_db()
        logger.info("Application shutdown completed")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
