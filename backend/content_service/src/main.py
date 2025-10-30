import asyncio

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from logger import get_logger
from proto.content_pb2 import DESCRIPTOR
from proto.content_pb2_grpc import add_ContentServiceServicer_to_server
from service.content_service import ContentService
from service.database import db_manager
from settings import settings

logger = get_logger("Main")


class HealthServicer(health_pb2_grpc.HealthServicer):
    """gRPC health check servicer implementation for database connectivity.

    Implements the Health service Check method to verify database connectivity
    and report service health status.

    Methods:
        Check: Performs health check by testing database connection.
    """

    async def Check(self, request, context):
        """Performs health check by testing database connectivity.

        Args:
            request: The health check request object.
            context: gRPC servicer context.

        Returns:
            health_pb2.HealthCheckResponse: Health check response with status:
                - SERVING if database ping succeeds
                - NOT_SERVING if database ping fails

        Note:
            Uses MongoDB's ping command to verify database connectivity.
            Returns NOT_SERVING status for any exception during ping.
        """
        try:
            await db_manager.db.command("ping")
            return health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.SERVING
            )
        except Exception:
            return health_pb2.HealthCheckResponse(
                status=health_pb2.HealthCheckResponse.NOT_SERVING
            )


async def serve() -> None:
    """Starts and runs the gRPC server for Content service.

    Initializes database connection and gRPC server with service registration
    and reflection. Manages server lifecycle and graceful shutdown.

    Raises:
        Exception: Any exception encountered during server startup that
        prevents the server from starting properly.

    Note:
        - Establishes database connection before starting services
        - Registers HealthServicer and ContentService with gRPC server
        - Enables server reflection for service discovery
        - Uses configuration from settings for server address
        - Ensures proper cleanup of database connection on shutdown
    """
    try:
        await db_manager.connect()
        logger.info("Database connection established")

        server = grpc.aio.server()

        health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
        add_ContentServiceServicer_to_server(ContentService(), server)

        service_names = (
            DESCRIPTOR.services_by_name["ContentService"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)

        server_address = (
            f"{settings.GRPC_CONTENT_HOST}:{settings.GRPC_CONTENT_PORT}"
        )
        server.add_insecure_port(server_address)
        await server.start()

        logger.info(f"gRPC server started on {server_address}")

        await server.wait_for_termination()

    except Exception as e:
        logger.exception(f"Failed to start server: {e}")
        raise
    finally:
        await db_manager.disconnect()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(serve())
