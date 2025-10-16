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
    """
    gRPC client for content service.

    This class establishes an insecure gRPC channel to the content service
    and creates a stub for making RPC calls related to content operations.

    Attributes:
        channel: gRPC insecure channel to the content service
        stub: ContentServiceStub instance for making gRPC calls to content service

    Note:
        - Uses insecure channel (no SSL/TLS) for connection
        - Connection details are taken from application settings for content service
    """

    def __init__(self):
        self.channel = grpc.insecure_channel(
            f"{settings.API_GATEWAY_CONTENT_HOST}:{settings.GRPC_CONTENT_PORT}"
        )
        self.stub = ContentServiceStub(self.channel)
        logger.info("ContentClient initialized")

    def get_about(self, lang: str = None):
        """
        Retrieve about page content in specified language.

        Args:
            lang (str, optional): Language code for the about content (e.g., 'en', 'ru').
                                 Defaults to None for default language.

        Returns:
            AboutResponse: gRPC response containing the about page content.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during content retrieval.

        Note:
            - Logs the language parameter and operation completion for monitoring
            - Returns localized content based on the provided language code
        """
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
        """
        Retrieve technology stack information.

        Returns:
            TechResponse: gRPC response containing technology stack data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during technology data retrieval.

        Note:
            - Logs the operation start and completion for monitoring
            - Typically returns information about technologies used in the project
        """
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
        """
        Retrieve projects list with optional language and sorting.

        Args:
            lang (str, optional): Language code for localized project content.
                                 Defaults to None for default language.
            sort (str, optional): Sorting criteria for projects (e.g., 'date', 'name').
                                 Defaults to None for default sorting.

        Returns:
            ProjectsResponse: gRPC response containing the list of projects.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during projects retrieval.

        Note:
            - Logs the language, sort parameters and operation completion for monitoring
            - Returns localized and sorted projects based on provided parameters
        """
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
        """
        Retrieve certificates list with optional sorting.

        Args:
            sort (str, optional): Sorting criteria for certificates (e.g., 'date', 'name').
                                 Defaults to None for default sorting.

        Returns:
            CertificatesResponse: gRPC response containing the list of certificates.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during certificates retrieval.

        Note:
            - Logs the sort parameter and operation completion for monitoring
            - Returns sorted certificates based on the provided criteria
        """
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
        """
        Retrieve publications list with optional language and sorting.

        Args:
            lang (str, optional): Language code for localized publication content.
                                 Defaults to None for default language.
            sort (str, optional): Sorting criteria for publications (e.g., 'date', 'title').
                                 Defaults to None for default sorting.

        Returns:
            PublicationsResponse: gRPC response containing the list of publications.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during publications retrieval.

        Note:
            - Logs the language, sort parameters and operation completion for monitoring
            - Returns localized and sorted publications based on provided parameters
        """
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
