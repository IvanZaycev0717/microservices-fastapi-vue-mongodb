import grpc
from grpc import ServicerContext

from logger import get_logger
from proto import content_pb2
from proto.content_pb2_grpc import ContentServiceServicer
from service.database import db_manager
from settings import settings

logger = get_logger(f"{settings.CONTENT_SERVICE_NAME} - Server")


class ContentService(ContentServiceServicer):
    """gRPC service for content operations."""
    async def GetAbout(
        self, request: content_pb2.AboutRequest, context: ServicerContext
    ) -> content_pb2.AboutResponse:
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

    async def GetTech(self, request: content_pb2.TechRequest, context: ServicerContext) -> content_pb2.TechResponse:
        """Retrieves all technology skills."""
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
        """Retrieves projects with language and sorting.

        Args:
            request: Projects request with language and sort parameters.
            context: gRPC servicer context.

        Returns:
            Projects response with list of project items.
        """
        try:
            logger.info(
                f"GetProjects called with lang: {request.lang}, sort: {request.sort}"
            )
            project_docs = await db_manager.get_projects(
                lang=request.lang or "en", sort=request.sort or "date_desc"
            )

            project_items = []
            for doc in project_docs:
                project_items.append(
                    content_pb2.ProjectItem(
                        id=doc.id,
                        title=doc.title if isinstance(doc.title, str) else "",
                        thumbnail=doc.thumbnail,
                        image=doc.image,
                        description=doc.description
                        if isinstance(doc.description, str)
                        else "",
                        link=doc.link,
                        date=doc.date.isoformat(),
                        popularity=doc.popularity,
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
        """Retrieves certificates with sorting.

        Args:
            request: Certificates request with sort parameter.
            context: gRPC servicer context.

        Returns:
            Certificates response with list of certificate items.
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
        """Retrieves publications with language and sorting.

        Args:
            request: Publications request with language and sort parameters.
            context: gRPC servicer context.

        Returns:
            Publications response with list of publication items.
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
