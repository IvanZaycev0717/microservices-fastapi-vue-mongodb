# API Gateway

Микросервис API Gateway на FastAPI для агрегации запросов к сервисам аутентификации, контента и комментариев.

## Функциональность

- **Аутентификация** - регистрация, вход, выход, обновление токенов
- **Контент** - информация "о себе", технологии, проекты, сертификаты, публикации  
- **Комментарии** - CRUD операции для комментариев к проектам
- **Кэширование** - Redis-кэш для контентных эндпоинтов
- **Rate Limiting** - ограничение запросов по токен-бакет алгоритму
- **Инвалидация кэша** - Kafka-консьюмер для очистки кэша

## Технологии

- FastAPI 0.119.0
- gRPC для межсервисной коммуникации
- Redis для кэширования и rate limiting
- Kafka для инвалидации кэша
- Pydantic для валидации данных
- Uvicorn для ASGI-сервера

## Запуск

### Docker
```bash
docker build -t api-gateway .
docker run -p 50055:50055 api-gateway
```

### Локально
```bash
poetry install
poetry run python src/main.py
```

## API Endpoints

### Аутентификация
- `POST /api/v1/login` - вход
- `POST /api/v1/register` - регистрация  
- `POST /api/v1/refresh` - обновление токенов
- `POST /api/v1/logout` - выход
- `POST /api/v1/verify` - верификация токена

### Контент
- `GET /api/v1/about` - информация "о себе"
- `GET /api/v1/tech` - стек технологий
- `GET /api/v1/projects` - проекты
- `GET /api/v1/certificates` - сертификаты
- `GET /api/v1/publications` - публикации

### Комментарии
- `GET /api/v1/comments` - все комментарии
- `GET /api/v1/comments/my` - комментарии пользователя
- `GET /api/v1/comments/project/{id}` - комментарии проекта
- `POST /api/v1/comments` - создать комментарий
- `PUT /api/v1/comments/{id}` - обновить комментарий
- `DELETE /api/v1/comments/{id}` - удалить комментарий

### Health Check
- `GET /health` - статус сервиса

## Конфигурация

Настройки через environment variables:

```bash
# API Gateway
API_GATEWAY_NAME=API Gateway
API_GATEWAY_HOST=0.0.0.0
API_GATEWAY_PORT=50055

# CORS
API_GATEWAY_FRONTENT_URL=http://localhost:3000

# Service Hosts
API_GATEWAY_CONTENT_HOST=content-service
API_GATEWAY_AUTH_HOST=auth-service  
API_GATEWAY_COMMENTS_HOST=comments-service

# Service Ports
GRPC_CONTENT_PORT=50051
GRPC_AUTH_PORT=50052
GRPC_COMMENTS_PORT=50053

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CACHE_INVALIDATION_TOPIC=cache-invalidation
```