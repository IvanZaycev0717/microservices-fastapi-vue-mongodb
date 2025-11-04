# Admin Service

Микросервис администрирования для управления контентом персонального сайта. Объединяет функциональность аутентификации, контента, комментариев и уведомлений в единой админ-панели.

## Технологии

- **FastAPI** - ASGI веб-фреймворк
- **PostgreSQL** - реляционная БД для комментариев
- **MongoDB** - документная БД для контента и пользователей
- **MinIO** - объектное хранилище для изображений
- **Kafka** - потоковая обработка логов и инвалидация кэша
- **Poetry** - управление зависимостями

## Запуск

### Docker
```bash
docker build -t admin-service .
docker run -p 8000:8000 admin-service
```

### Локально
```bash
poetry install
poetry run python src/main.py
```

## API Endpoints

### Контент
- `GET/POST/PATCH /about` - информация "о себе"
- `GET/PATCH /technologies/{kingdom}` - стек технологий  
- `GET/POST/PATCH /projects` - управление проектами
- `GET/POST/PATCH /certificates` - сертификаты
- `GET/POST/PATCH /publications` - публикации

### Аутентификация
- `POST /auth/login` - вход в систему
- `POST /auth/refresh` - обновление токенов
- `POST /auth/logout` - выход
- `POST /auth/register` - регистрация
- `GET/PATCH/DELETE /auth` - управление пользователями

### Комментарии
- `GET/POST/PATCH/DELETE /comments` - модерация комментариев

### Уведомления  
- `GET/POST/DELETE /notifications` - управление нотификациями

## Конфигурация

Основные environment variables:

```bash
# Service
ADMIN_SERVICE_HOST=0.0.0.0
ADMIN_SERVICE_PORT=8000

# Databases
CONTENT_ADMIN_MONGODB_URL=mongodb://...
AUTH_ADMIN_MONGODB_URL=mongodb://...
COMMENTS_ADMIN_POSTGRES_DB_URL=postgresql://...

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Storage
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```