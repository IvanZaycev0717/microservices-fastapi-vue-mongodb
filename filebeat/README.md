# Filebeat для реализации Elastic Stack

Конфигурация Filebeat для сбора логов из Kafka и отправки в Elasticsearch.

## Назначение

Filebeat используется как log shipper для:
- Потребления логов из Kafka-топиков
- Парсинга JSON-сообщений
- Отправки структурированных логов в Elasticsearch

## Конфигурация

### Входные данные (Inputs)
```yaml
- type: kafka
  hosts: ["broker-1:19092", "broker-2:19092", "broker-3:19093"]
  topics: ["admin_service_logs"]
  group_id: "filebeat"
  consumer_group: "filebeat-logs-group"
```

### Обработка (Processors)
```yaml
- decode_json_fields:
    fields: ["message"]
    target: ""  # Парсинг JSON в корень документа
    overwrite_keys: true
    add_error_key: true
```

### Выходные данные (Output)
```yaml
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "admin_service_logs"  # Индекс в Elasticsearch
  protocol: "http"
```

## Запуск

### Docker
```bash
docker build -t filebeat-custom .
docker run --network=host filebeat-custom
```

## Особенности

- **Kafka Consumer**: Подключение к кластеру из 3 брокеров
- **JSON Parsing**: Автоматический парсинг JSON-логов из сообщений Kafka
- **Elasticsearch Integration**: Прямая отправка в Elasticsearch
- **Debug Logging**: Подробное логирование работы Filebeat

## Интеграция

Собирает логи из топика `admin_service_logs` и отправляет в индекс Elasticsearch с тем же именем. Используется для централизованного сбора логов со всех микросервисов бекенда.