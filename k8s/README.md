# Kubernetes Deployment

Микросервисное приложение развернутое в Minikube Kubernetes кластере. Включает фронтенд на Vue.js, бэкенд на FastAPI, базы данных MongoDB/PostgreSQL, Kafka для асинхронной коммуникации и MinIO для хранения файлов.

## 🏗️ Архитектура

### Сервисы
- **Frontend** (Vue 3) - порт 30000
- **API Gateway** - порт 30055  
- **Admin GUI** - порт 30080
- **Content Service** - управление контентом
- **Auth Service** - аутентификация и авторизация
- **Comments Service** - управление комментариями
- **Notification Service** - email уведомления

### Базы данных
- **MongoDB** ×3 (content, auth, notification)
- **PostgreSQL** - комментарии
- **Redis** - кеширование

### Инфраструктура
- **Kafka** (3 брокера + 3 контроллера) - асинхронная коммуникация
- **MinIO** - объектное хранилище
- **Nginx** - reverse proxy для фронтенда

## 📋 Требования

- Minikube v1.37.0+
- Kubernetes v1.34+
- Docker
- 4GB+ RAM (рекомендуется 8GB)

## 🚀 Быстрый старт

### 1. Запуск Minikube
```bash
minikube start --memory=8192 --cpus=4
```

### 2. Сборка Docker образов
```bash
# Сборка всех сервисов
docker build -t frontend:latest ./frontend
docker build -t api-gateway:latest ./backend/api_gateway
docker build -t content-service:latest ./backend/content_service
docker build -t auth-service:latest ./backend/auth_service
docker build -t comments-service:latest ./backend/comments_service
docker build -t notification-service:latest ./backend/notification_service
docker build -t admin-service:latest ./backend/admin_service/src
docker build -t admin-gui:latest ./backend/admin_service/admin_gui
```

### 3. Деплой в Kubernetes
```bash
# Применение манифестов в правильном порядке
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mongo-init.yaml
kubectl apply -f k8s/postgres-init.yaml
kubectl apply -f k8s/databases.yaml
kubectl apply -f k8s/minio.yaml
kubectl apply -f k8s/frontend-config.yaml
kubectl apply -f k8s/frontend-nginx-config.yaml
kubectl apply -f k8s/admin-gui-nginx-config.yaml
kubectl apply -f src/kafka.yaml
kubectl apply -f k8s/services.yaml
```

### 4. Проверка статуса
```bash
kubectl get pods -n microservices-app -w
```

## 🌐 Доступ к приложению

После успешного деплоя откройте сервисы в браузере:

```bash
# Frontend приложение
minikube service -n microservices-app frontend

# API Gateway (для тестирования API)
minikube service -n microservices-app api-gateway

# Admin панель
minikube service -n microservices-app admin-gui
```

**URLs:**
- Frontend: `http://localhost:30000`
- API Gateway: `http://localhost:30055` 
- Admin GUI: `http://localhost:30080`

## 🔧 Конфигурация

### Environment Variables
Основные настройки в `k8s/configmap.yaml`:
- `MINIO_PUBLIC_URL` - URL для доступа к MinIO
- `FRONTEND_URL` - базовый URL фронтенда
- `KAFKA_BOOTSTRAP_SERVERS` - настройки Kafka
- Настройки баз данных и сервисов

### Secrets
Конфиденциальные данные в `k8s/secrets.yaml`:
- Пароли баз данных
- SMTP настройки для email
- JWT секреты
- MinIO credentials

## 🗄️ Базы данных

### MongoDB
- **content_db** - данные контента
- **auth_db** - пользователи и аутентификация  
- **notification_db** - уведомления

### PostgreSQL
- **comments_db** - комментарии и связанные данные

### Инициализация
Базы данных автоматически инициализируются скриптами из:
- `k8s/mongo-init.yaml` - пользователи MongoDB
- `k8s/postgres-init.yaml` - схема PostgreSQL

## 📧 Уведомления

Notification Service обрабатывает:
- Запросы сброса пароля
- Подтверждения сброса пароля
- Использует Kafka для асинхронной обработки

### Настройка Email
В `k8s/secrets.yaml` укажите SMTP настройки:
```yaml
SMTP_USERNAME: "your-email@domain.com"
SMTP_PASSWORD: "your-password"
SMTP_FROM: "your-email@domain.com"
```

## 🔄 Мониторинг и логи

Просмотр логов любого сервиса:
```bash
kubectl logs -n microservices-app deployment/frontend -f
kubectl logs -n microservices-app deployment/api-gateway -f
# ... и т.д.
```

## 🛠️ Управление

### Масштабирование сервисов
```bash
kubectl scale deployment/frontend --replicas=3 -n microservices-app
```

### Перезапуск сервисов
```bash
kubectl rollout restart deployment/frontend -n microservices-app
```

### Обновление конфигурации
```bash
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment -n microservices-app
```

## 🚨 Troubleshooting

### Проблемы с Kafka
Если notification-service отправляет дублирующиеся письма:
```bash
# Очистка топиков Kafka
kubectl exec -n microservices-app -it kafka-broker-0 -- /bin/bash
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:19092 --delete --topic password-reset-requests
/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:19092 --delete --topic password-reset-success
```

### Проблемы с базами данных
Очистка и переинициализация:
```bash
kubectl exec -n microservices-app -it content-db-0 -- mongosh -u admin -p securepassword123 --authenticationDatabase admin --eval "use content_db; db.about.deleteMany({});"
```

### Проблемы с образами
Убедитесь что все образы собраны с тегом `latest` и `imagePullPolicy: Never`

## 📁 Структура проекта

```
k8s/
├── configmap.yaml          # Основные настройки
├── secrets.yaml           # Секретные данные
├── databases.yaml         # Базы данных (MongoDB, PostgreSQL, Redis)
├── services.yaml          # Микросервисы приложения
├── minio.yaml            # Object storage
├── kafka.yaml           # Kafka brokers and controllers
├── frontend-config.yaml  # Frontend configuration
└── *-nginx-config.yaml   # Nginx proxy configurations

src/
└── kafka.yaml           # Kafka configuration

backend/                 # Микросервисы бэкенда
frontend/               # Vue.js приложение
```

## 🔄 Процесс разработки

1. Внесите изменения в код
2. Пересоберите Docker образ: `docker build -t service-name:latest ./path`
3. Примените манифесты: `kubectl apply -f k8s/`
4. Перезапустите сервис: `kubectl rollout restart deployment/service-name`

## 📞 Поддержка

При возникновении проблем проверьте:
1. Статус всех подов: `kubectl get pods -n microservices-app`
2. Логи проблемного сервиса
3. Доступность баз данных и Kafka
4. Корректность конфигурации в configmap и secrets