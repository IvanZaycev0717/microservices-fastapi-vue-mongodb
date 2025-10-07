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

logger = get_logger(f"{settings.GRPC_CONTENT_SERVICE_NAME} - Main")


class HealthServicer(health_pb2_grpc.HealthServicer):
    async def Check(self, request, context):
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
    """Starts the gRPC server and manages database connection."""
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

        server_address = f"{settings.GRPC_CONTENT_HOST}:{settings.GRPC_CONTENT_PORT}"
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
