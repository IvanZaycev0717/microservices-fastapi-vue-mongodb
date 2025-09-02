import grpc
from generated import about_pb2, about_pb2_grpc


class AboutClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(f"{'localhost'}:{50051}")
        self.stub = about_pb2_grpc.AboutServiceStub(self.channel)

    def get_about(self, lang: str = "en"):
        try:
            request = about_pb2.AboutRequest(lang=lang)
            response = self.stub.GetAbout(request)
            return self._parse_response(response)
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            return None

    def _parse_response(self, response):
        items = []
        for item in response.items:
            items.append(
                {
                    "image": item.image,
                    "title": item.translation.title,
                    "description": item.translation.description,
                }
            )

        return items

    def close(self):
        self.channel.close()


if __name__ == "__main__":
    client = AboutClient()
    try:
        print("Testing gRPC client...")
        result = client.get_about("en")
        print("English result:", result)

        result_ru = client.get_about("ru")
        print("Russian result:", result_ru)
    finally:
        client.close()
