# Auth Service

Микросервис аутентификации на gRPC для управления пользователями, токенами и безопасностью.

## Функциональность

- **Регистрация и аутентификация** - создание пользователей, вход с email/password
- **Управление токенами** - JWT access/refresh токены, верификация, обновление
- **Восстановление пароля** - генерация reset-токенов, безопасная смена пароля
- **Безопасность** - хеширование паролей bcrypt, инвалидация токенов, бан пользователей
- **Асинхронная коммуникация** - Kafka для отправки уведомлений о сбросе пароля

## Технологии

- gRPC для API
- MongoDB для хранения пользователей и токенов
- JWT для токенов аутентификации
- bcrypt для хеширования паролей
- Kafka для асинхронных сообщений
- Pydantic для валидации данных

## Запуск

### Docker
```bash
docker build -t auth-service .
docker run -p 50052:50052 auth-service
```

### Локально
```bash
poetry install
poetry run python src/main.py
```

## gRPC API

### Аутентификация
- `Login` - вход пользователя, возвращает access/refresh токены
- `Register` - регистрация нового пользователя
- `Logout` - выход и инвалидация refresh токена

### Управление токенами
- `RefreshToken` - обновление access токена с помощью refresh токена
- `VerifyToken` - верификация JWT токена и извлечение claims

### Восстановление пароля
- `ForgotPassword` - запрос сброса пароля, генерация reset токена
- `ResetPassword` - смена пароля с использованием reset токена

## Конфигурация

Environment variables:

```bash
# MongoDB
GRPC_AUTH_MONGODB_URL=mongodb://user:pass@mongodb:27017
GRPC_AUTH_MONGODB_DB_NAME=auth_db

# Service
GRPC_AUTH_NAME=Auth Service
GRPC_AUTH_GRPC_HOST=0.0.0.0
GRPC_AUTH_PORT=50052

# Security
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=15

# Password Constraints
MIN_PASSWORD_LENGTH=8
MAX_PASSWORD_LENGTH=128
MIN_EMAIL_LENGTH=5
MAX_EMAIL_LENGTH=255

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_PASSWORD_RESET_TOPIC=password-reset-requests
KAFKA_PASSWORD_RESET_SUCCESS_TOPIC=password-reset-success
```

## Модели данных

### Пользователь
- `id` - уникальный идентификатор
- `email` - email пользователя
- `password_hash` - хеш пароля
- `roles` - роли пользователя
- `is_banned` - статус бана
- `created_at` - дата создания
- `last_login_at` - последний вход

### Токены
- Refresh токены с expiration
- Reset токены для восстановления пароля
- Автоматическая инвалидация использованных токенов

## Безопасность

- Пароли хешируются с bcrypt (12 rounds)
- JWT токены подписываются секретным ключом
- Refresh токены хранятся в БД с expiration
- Валидация email и паролей по длине и формату
- Защита от повторного использования токенов

## Тестирование

```bash
# Запуск всех тестов
pytest src/tests/

# Запуск конкретного тестового файла
pytest src/tests/test_database.py

# С подробным выводом
pytest -v

# С покрытием кода
pytest --cov=src

# С покрытием кода
pytest --cov=src
```
## Структура тестов
`src/tests/conftest.py` - фикстуры и настройка окружения

`src/tests/test_database.py` - тесты операций с базой данных

Моки MongoDB для изолированного тестирования