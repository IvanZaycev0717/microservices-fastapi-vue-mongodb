# Admin GUI

Фронтенд-часть Admin Service для управления контентом персонального сайта. SPA-приложение на Quasar Framework (Vue 3) с административным интерфейсом.

## Функциональность

- **Аутентификация** - вход, выход, обновление токенов, управление доступом
- **Управление контентом** - информация "о себе", технологии, проекты, сертификаты, публикации
- **Модерация** - управление комментариями и пользователями
- **Уведомления** - система оповещений и нотификаций
- **Администрирование** - CRUD операции для всего контента

## Технологии

- Quasar Framework 2.16.0
- Vue 3.5.20
- Pinia для управления состоянием
- Vue Router для навигации
- Axios для HTTP-запросов
- Nginx для раздачи статики

## Запуск

### Разработка
```bash
npm install
npm run dev
```

### Сборка
```bash
npm run build
```

### Docker
```bash
docker build -t admin-gui .
docker run -p 80:80 admin-gui
```

## API Интеграция

Приложение взаимодействует с бекенд-сервисом на `localhost:8000`:

### Аутентификация
- `POST /auth/login` - вход в систему
- `POST /auth/refresh` - обновление токенов
- `POST /auth/logout` - выход из системы

### Контент
- `GET/POST/PATCH /about` - управление информацией "о себе"
- `GET/POST/PATCH /projects` - управление проектами
- `GET/POST/PATCH /certificates` - управление сертификатами
- `GET/POST/PATCH /publications` - управление публикациями
- `PATCH /technologies/{kingdom}` - обновление технологий

### Администрирование
- `GET/POST/DELETE /auth` - управление пользователями
- `GET/POST/PATCH/DELETE /comments` - модерация комментариев
- `GET/POST/DELETE /notifications` - управление уведомлениями

## Конфигурация

### Environment Variables
```bash
# Бекенд API
API_BASE_URL=http://localhost:8000

# Режим сборки
NODE_ENV=production

# Настройки Quasar
QUASAR_MODE=spa
```

### Настройки Nginx
Конфигурация для раздачи SPA включена в `nginx.conf`:
- Обслуживание статических файлов
- Поддержка history mode роутинга
- Настройки кэширования

## Требования

- Node.js ^20 || ^22 || ^24
- npm >= 6.13.4
- Бекенд-сервис на порту 8000