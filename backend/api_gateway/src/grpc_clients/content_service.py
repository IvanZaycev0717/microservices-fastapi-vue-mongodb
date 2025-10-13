import grpc
from protos.content_service_pb2 import (
    AboutRequest,
    TechRequest,
    ProjectsRequest,
    CertificatesRequest,
    PublicationsRequest,
)
from protos.content_service_pb2_grpc import ContentServiceStub
from settings import settings
from logger import get_logger

logger = get_logger("ContentClient")


class ContentClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(
            f"{settings.GRPC_CONTENT_HOST}:{settings.GRPC_CONTENT_PORT}"
        )
        self.stub = ContentServiceStub(self.channel)
        logger.info("ContentClient initialized")

    def get_about(self, lang: str = None):
        try:
            logger.info(f"get_about called with lang: {lang}")
            request = AboutRequest(lang=lang or "")
            response = self.stub.GetAbout(request)
            logger.info("get_about completed successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_about: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_about: {e}")
            raise

    def get_tech(self):
        try:
            logger.info("get_tech called")
            request = TechRequest()
            response = self.stub.GetTech(request)
            logger.info("get_tech completed successfully")
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_tech: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_tech: {e}")
            raise

    def get_projects(self, lang: str = None, sort: str = None):
        try:
            logger.info(f"get_projects called with lang: {lang}, sort: {sort}")
            request = ProjectsRequest(lang=lang or "", sort=sort or "")
            response = self.stub.GetProjects(request)
            logger.info("get_projects completed successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_projects: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_projects: {e}")
            raise

    def get_certificates(self, sort: str = None):
        try:
            logger.info(f"get_certificates called with sort: {sort}")
            request = CertificatesRequest(sort=sort or "")
            response = self.stub.GetCertificates(request)
            logger.info("get_certificates completed successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_certificates: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_certificates: {e}")
            raise

    def get_publications(self, lang: str = None, sort: str = None):
        try:
            logger.info(
                f"get_publications called with lang: {lang}, sort: {sort}"
            )
            request = PublicationsRequest(lang=lang or "", sort=sort or "")
            response = self.stub.GetPublications(request)
            logger.info("get_publications completed successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_publications: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_publications: {e}")
            raise
