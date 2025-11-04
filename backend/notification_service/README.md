# Notification Service

Микросервис уведомлений на FastAPI для обработки и отправки email-уведомлений через Kafka.

## Функциональность

- **Асинхронная обработка сообщений** - потребление событий из Kafka
- **Email-уведомления** - отправка HTML-писем через SMTP
- **Шаблонизация** - готовые HTML-шаблоны для писем
- **Отслеживание статусов** - сохранение статусов отправки в MongoDB
- **Health-check** - эндпоинты для мониторинга состояния сервиса

## Технологии

- FastAPI для HTTP API
- MongoDB для хранения уведомлений
- Kafka для асинхронных сообщений
- SMTP для отправки email
- AIOKafka для асинхронного потребления
- Pydantic для валидации данных

## Запуск

### Docker
```bash
docker build -t notification-service .
docker run -p 8000:8000 notification-service
```

### Локально
```bash
poetry install --only main
poetry run python src/main.py
```

## API Endpoints

### Health Check
- `GET /health` - статус сервиса
- `GET /` - базовая информация о сервисе

## Обработка событий Kafka

### Темы
- `password-reset-requests` - запросы сброса пароля
- `password-reset-success` - успешный сброс пароля

### Типы уведомлений
- `reset_request` - письмо со ссылкой сброса пароля
- `reset_success` - подтверждение успешной смены пароля

## Конфигурация

Environment variables:

```bash
# MongoDB
NOTIFICATION_SERVICE_MONGODB_URL=mongodb://user:pass@mongodb:27017
NOTIFICATION_SERVICE_MONGO_DATABASE_NAME=notifications_db

# Service
NOTIFICATION_SERVICE_NAME=Notification Service
NOTIFICATION_HOST=0.0.0.0
NOTIFICATION_PORT=8000
SERVICE_NAME=NOTIFICATION_SERVICE
LOG_LEVEL=INFO

# MongoDB Timeouts
MONGO_CONNECTION_TIMEOUT_MS=10000
MONGO_SERVER_SELECTION_TIMEOUT_MS=10000

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_PASSWORD_RESET_TOPIC=password-reset-requests
KAFKA_PASSWORD_RESET_SUCCESS_TOPIC=password-reset-success

# SMTP
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@domain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465

# Validation
MIN_EMAIL_SUBJECT_LENGTH=1
MAX_EMAIL_SUBJECT_LENGTH=255
MIN_EMAIL_MESSAGE_LENGTH=1
MAX_EMAIL_MESSAGE_LENGTH=5000
```

## Модели данных

### Уведомление
- `_id` - уникальный идентификатор
- `to_email` - email получателя
- `subject` - тема письма
- `message` - текст сообщения
- `status` - статус отправки (pending/sent/failed)
- `message_type` - тип уведомления
- `user_id` - ID пользователя
- `created_at` - дата создания
- `sent_at` - дата отправки

## Шаблоны email

### Сброс пароля
- HTML-шаблон с CSS-стилизацией
- Кнопка для сброса пароля
- Токен сброса в ссылке

### Успешный сброс
- Подтверждение изменения пароля
- Ссылка для входа в аккаунт

## Особенности

- Полностью асинхронная архитектура
- JSON-логирование для структурированного анализа
- Обработка ошибок при отправке email
- Кэширование CSS-стилей для шаблонов
- Graceful shutdown при остановке сервиса