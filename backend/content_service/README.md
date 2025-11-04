# Content Service

gRPC микросервис для управления контентом. Предоставляет данные о проектах, технологиях, сертификатах и публикациях.

## Технологии

- Python 3.12
- gRPC
- MongoDB (Async)
- Pydantic
- Poetry
- Docker

## Запуск

```bash
docker build -t content-service .
docker run -p 50051:50051 content-service
```

## gRPC API

### Методы

- `GetAbout(lang)` - информация "О себе" с поддержкой языков
- `GetTech()` - стек технологий по категориям
- `GetProjects(lang, sort)` - проекты с сортировкой
- `GetCertificates(sort)` - сертификаты
- `GetPublications(lang, sort)` - публикации

### Поддерживаемые языки
- `en` (по умолчанию)
- `ru`

### Сортировка
- `date_desc`/`date_asc`
- `popularity_desc`/`popularity_asc`
- `rating_desc`/`rating_asc`

## Конфигурация

Обязательные переменные окружения:
```bash
GRPC_CONTENT_MONGODB_URL
GRPC_CONTENT_MONGODB_DB_NAME
GRPC_CONTENT_HOST
GRPC_CONTENT_PORT
```

## Health Check

Сервис включает gRPC health checking. Endpoint: `grpc.health.v1.Health`

## Тестирование

```bash
# Запуск всех тестов
pytest src/tests/

# С подробным выводом
pytest -v

# С покрытием кода
pytest --cov=src

# С покрытием кода
pytest --cov=src
```