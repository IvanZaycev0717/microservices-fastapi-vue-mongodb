# Comments Service

Микросервис комментариев на gRPC для управления иерархическими комментариями с хранением в PostgreSQL.

## Функциональность

- **Создание комментариев** - добавление комментариев и ответов к проектам
- **Иерархические комментарии** - поддержка цепочек ответов (родитель-потомок)
- **Поиск и фильтрация** - получение комментариев по проекту, автору, ID
- **Управление комментариями** - обновление текста, удаление с каскадом
- **Безопасность** - валидация данных, HTML-экранирование

## Технологии

- gRPC для API
- PostgreSQL для хранения комментариев
- SQLAlchemy 2.0 для асинхронной работы с БД
- Pydantic для валидации данных
- AsyncPG для асинхронных запросов

## Запуск

### Docker
```bash
docker build -t comments-service .
docker run -p 50054:50054 comments-service
```

### Локально
```bash
poetry install
poetry run python src/main.py
```

## gRPC API

### Основные операции
- `CreateComment` - создание комментария/ответа
- `GetComment` - получение комментария по ID
- `GetAllComments` - все комментарии (с пагинацией)
- `UpdateComment` - обновление текста комментария
- `DeleteComment` - удаление с каскадным удалением ответов

### Поиск и фильтрация
- `GetCommentsByProjectId` - комментарии конкретного проекта
- `GetCommentsByAuthorId` - комментарии конкретного автора

## Конфигурация

Environment variables:

```bash
# PostgreSQL
GRPC_COMMENTS_POSTGRES_URL=postgresql+asyncpg://user:pass@postgres:5432/comments
POSTGRES_USER=user
POSTGRES_PASSWORD=pass

# Service
GRPC_COMMENTS_SERVICE_NAME=Comments Service
GRPC_COMMENTS_HOST=0.0.0.0
GRPC_COMMENTS_PORT=50054
SERVICE_NAME=COMMENTS_SERVICE
LOG_LEVEL=INFO

# Database
POSTGRES_CONNECTION_TIMEOUT=30
POSTGRES_COMMAND_TIMEOUT=60
POSTGRES_POOL_MIN_SIZE=1
POSTGRES_POOL_MAX_SIZE=10

# Validation
COMMENTS_PROJECT_ID_LENGTH=24
COMMENTS_AUTHOR_ID_LENGTH=24
MIN_COMMENT_LENGTH=1
MAX_COMMENT_LENGTH=1000
MAX_EMAIL_LENGTH=255
MONGO_ID_VALID_ID_REGEXP=^[0-9a-fA-F]{24}$
```

## Модели данных

### Комментарий
- `id` - уникальный идентификатор
- `project_id` - ID проекта
- `author_id` - ID автора
- `author_email` - email автора
- `comment_text` - текст комментария
- `created_at` - дата создания
- `parent_comment_id` - родительский комментарий
- `likes` - количество лайков
- `dislikes` - количество дизлайков

## Безопасность

- Валидация ID по MongoDB-совместимому формату
- HTML-экранирование текста комментариев
- Валидация email и длины текста
- Каскадное удаление ответов при удалении родителя

## Особенности

- Полностью асинхронная архитектура
- Поддержка древовидной структуры комментариев
- JSON-логирование для структурированного анализа
- Health-check gRPC endpoints
- Рефлексия gRPC для тестирования и discovery