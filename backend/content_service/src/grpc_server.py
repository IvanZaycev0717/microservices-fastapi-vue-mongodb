import sys
import grpc
from concurrent import futures
import logging

from generated import about_pb2, about_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AboutServicer(about_pb2_grpc.AboutServiceServicer):
    def GetAbout(self, request, context):
        try:
            lang = request.lang or "en"
            logger.info(f"Getting about data for language: {lang}")

            # Заглушка с тестовыми данными
            items = self._get_about_data(lang)

            return self._create_response(items)

        except Exception as e:
            logger.error(f"Error in GetAbout: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return about_pb2.AboutResponse()

    def _get_about_data(self, lang: str):
        # Заглушка - здесь будет реальная логика из БД
        db_data = [
            {
                "image": "image_1.jpg",
                "translations": {
                    "en": {
                        "title": "Some title 1 EN",
                        "description": "Some description 1 EN",
                    },
                    "ru": {"title": "Название 1 RU", "description": "Описание 1 RU"},
                },
            },
            {
                "image": "image_2.jpg",
                "translations": {
                    "en": {
                        "title": "Some title 2 EN",
                        "description": "Some description 2 EN",
                    },
                    "ru": {"title": "Название 2 RU", "description": "Описание 2 RU"},
                },
            },
        ]

        filtered_items = []
        for item in db_data:
            translation = (
                item["translations"].get(lang)
                or item["translations"].get("en")
                or next(iter(item["translations"].values()))
            )
            filtered_items.append(
                {
                    "image": item["image"],
                    "title": translation["title"],
                    "description": translation["description"],
                }
            )

        return filtered_items

    def _create_response(self, items):
        response = about_pb2.AboutResponse()

        for item in items:
            about_item = response.items.add()
            about_item.image = item["image"]
            about_item.translation.title = item["title"]
            about_item.translation.description = item["description"]

        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    about_pb2_grpc.add_AboutServiceServicer_to_server(AboutServicer(), server)

    port = 50051

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server started on port {port}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        logger.info("gRPC server stopped")


if __name__ == "__main__":
    serve()
