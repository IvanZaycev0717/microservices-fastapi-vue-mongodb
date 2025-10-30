import grpc
from grpc import ServicerContext

from logger import get_logger
from proto import content_pb2
from proto.content_pb2_grpc import ContentServiceServicer
from service.database import db_manager

logger = get_logger("Server")


class ContentService(ContentServiceServicer):
    async def GetAbout(
        self, request: content_pb2.AboutRequest, context: ServicerContext
    ) -> content_pb2.AboutResponse:
        """Retrieves about section content with language support.

        Fetches about documents and returns them in protobuf format,
        with optional language filtering for translations.

        Args:
            request: AboutRequest containing optional language parameter.
            context: gRPC servicer context for error handling.

        Returns:
            content_pb2.AboutResponse: Response containing about items
            with requested language translations.

        Note:
            - Returns all translations if no language specified
            - Filters to specific language translation if provided
            - Returns empty list if no about documents found
            - Handles internal errors with appropriate gRPC status codes
        """
        try:
            logger.info(f"GetAbout called with lang: {request.lang}")
            about_docs = await db_manager.get_about(request.lang or None)
            about_items = []
            for doc in about_docs:
                if request.lang and request.lang in doc.translations:
                    translation = doc.translations[request.lang]
                    about_items.append(
                        content_pb2.AboutItem(
                            id=doc.id,
                            image_url=doc.image_url,
                            title=translation.title,
                            description=translation.description,
                        )
                    )
                else:
                    for translation in doc.translations.values():
                        about_items.append(
                            content_pb2.AboutItem(
                                id=doc.id,
                                image_url=doc.image_url,
                                title=translation.title,
                                description=translation.description,
                            )
                        )

            return content_pb2.AboutResponse(about=about_items)

        except Exception as e:
            logger.exception(f"Error in GetAbout: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return content_pb2.AboutResponse()

    async def GetTech(
        self, request: content_pb2.TechRequest, context: ServicerContext
    ) -> content_pb2.TechResponse:
        """Retrieves technology stack organized by categories (kingdoms).

        Fetches the technology document and organizes all technology categories
        into a structured response for the client.

        Args:
            request: TechRequest (empty request).
            context: gRPC servicer context for error handling.

        Returns:
            content_pb2.TechResponse: Response containing all technology
            kingdoms and their items.

        Note:
            - Assumes single tech document in database (uses first document)
            - Organizes technologies into predefined kingdom categories
            - Returns empty response if no tech documents found
            - Handles internal errors with appropriate gRPC status codes
        """
        try:
            logger.info("GetTech called")
            tech_docs = await db_manager.get_tech()

            if not tech_docs:
                return content_pb2.TechResponse()

            tech_doc = tech_docs[0]
            kingdoms = []

            for field_name in [
                "backend_kingdom",
                "database_kingdom",
                "frontend_kingdom",
                "desktop_kingdom",
                "devops_kingdom",
                "telegram_kingdom",
                "parsing_kingdom",
                "computerscience_kingdom",
                "gamedev_kingdom",
                "ai_kingdom",
            ]:
                kingdom = getattr(tech_doc, field_name)
                kingdoms.append(
                    content_pb2.TechKingdom(
                        kingdom=kingdom.kingdom, items=kingdom.items
                    )
                )

            return content_pb2.TechResponse(kingdoms=kingdoms)

        except Exception as e:
            logger.exception(f"Error in GetTech: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return content_pb2.TechResponse()

    async def GetProjects(
        self, request: content_pb2.ProjectsRequest, context: ServicerContext
    ) -> content_pb2.ProjectsResponse:
        """Retrieves projects with language and sorting preferences.

        Fetches projects from database and returns them in protobuf format
        with applied language translations and sorting.

        Args:
            request: ProjectsRequest containing language and sort parameters.
            context: gRPC servicer context for error handling.

        Returns:
            content_pb2.ProjectsResponse: Response containing project items
            with requested language and sorting.

        Note:
            - Applies language filtering to title and description fields
            - Supports sorting by date or popularity in ascending/descending order
            - Defaults to English language and date descending sort
            - Returns empty list if no projects found
            - Handles internal errors with appropriate gRPC status codes
        """
        try:
            logger.info(
                f"GetProjects called with lang: {request.lang}, sort: {request.sort}"
            )
            project_docs = await db_manager.get_projects(
                lang=request.lang or "en", sort=request.sort or "date_desc"
            )
            logger.warning(str(project_docs))
            project_items = []
            for doc in project_docs:
                project_items.append(
                    content_pb2.ProjectItem(
                        id=doc["id"],
                        title=doc["title"],
                        thumbnail=doc["thumbnail"],
                        image=doc["image"],
                        description=doc["description"],
                        link=doc["link"],
                        date=doc["date"],
                        popularity=doc["popularity"],
                    )
                )

            return content_pb2.ProjectsResponse(projects=project_items)

        except Exception as e:
            logger.exception(f"Error in GetProjects: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return content_pb2.ProjectsResponse()

    async def GetCertificates(
        self,
        request: content_pb2.CertificatesRequest,
        context: ServicerContext,
    ) -> content_pb2.CertificatesResponse:
        """Retrieves certificates with customizable sorting.

        Fetches certificate documents and returns them in protobuf format
        with applied sorting preferences.

        Args:
            request: CertificatesRequest containing optional sort parameter.
            context: gRPC servicer context for error handling.

        Returns:
            content_pb2.CertificatesResponse: Response containing certificate items
            with requested sorting applied.

        Note:
            - Supports sorting by date or popularity in ascending/descending order
            - Defaults to date descending sort if not specified
            - Converts date objects to ISO format strings
            - Returns empty list if no certificates found
            - Handles internal errors with appropriate gRPC status codes
        """
        try:
            logger.info(f"GetCertificates called with sort: {request.sort}")
            certificate_docs = await db_manager.get_certificates(
                sort=request.sort or "date_desc"
            )

            certificate_items = []
            for doc in certificate_docs:
                certificate_items.append(
                    content_pb2.CertificateItem(
                        id=doc.id,
                        thumb=doc.thumb,
                        src=doc.src,
                        date=doc.date.isoformat(),
                        popularity=doc.popularity,
                        alt=doc.alt,
                    )
                )

            return content_pb2.CertificatesResponse(
                certificates=certificate_items
            )

        except Exception as e:
            logger.exception(f"Error in GetCertificates: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return content_pb2.CertificatesResponse()

    async def GetPublications(
        self,
        request: content_pb2.PublicationsRequest,
        context: ServicerContext,
    ) -> content_pb2.PublicationsResponse:
        """Retrieves publications with language-specific titles and sorting.

        Fetches publication documents and returns them in protobuf format
        with applied language filtering and sorting preferences.

        Args:
            request: PublicationsRequest containing language and sort parameters.
            context: gRPC servicer context for error handling.

        Returns:
            content_pb2.PublicationsResponse: Response containing publication items
            with requested language and sorting.

        Note:
            - Applies language filtering to title field (English or Russian)
            - Supports sorting by date or rating in ascending/descending order
            - Defaults to English language and date descending sort
            - Converts date objects to ISO format strings
            - Returns empty string for title if translation not available
            - Returns empty list if no publications found
            - Handles internal errors with appropriate gRPC status codes
        """
        try:
            logger.info(
                f"GetPublications called with lang: {request.lang}, sort: {request.sort}"
            )
            publication_docs = await db_manager.get_publications(
                lang=request.lang or "en", sort=request.sort or "date_desc"
            )

            publication_items = []
            for doc in publication_docs:
                publication_items.append(
                    content_pb2.PublicationItem(
                        id=doc.id,
                        title=doc.title if isinstance(doc.title, str) else "",
                        page=doc.page,
                        site=doc.site,
                        rating=doc.rating,
                        date=doc.date.isoformat(),
                    )
                )

            return content_pb2.PublicationsResponse(
                publications=publication_items
            )

        except Exception as e:
            logger.exception(f"Error in GetPublications: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return content_pb2.PublicationsResponse()
