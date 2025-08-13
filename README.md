# Heroes-api


## Запуск тестов
Перейти в корневой каталог проекта и выполнить команду

### Запуск всех тестов
```bash 
  pytest
```

### Запуск Unit тестов
```bash
  pytest tests/test_api_unit.py
```
### Запуск интеграционных тестов
```bash
  pytest -tests/test_api_integration.py
```

## Запуск проекта
* Созадть .env файл в корневом каталоге проекта. В файле должны быть следующие переменные

```
DB_USER = "your_postgres_user"
DB_PASSWORD = "your_db_pass"
DB_HOST = "your_db_host"
DB_PORT = "your_db_port"
DB_NAME = "your_db_name"
API_ACCESS = "Your api access"
```
* В корневом каталоге проекта выполнить команды


```bash
  docker-compose build --no-cache
```

```bash
  docker-compose up -d
```

* После запуска api будет доступно по адресу `http://127.0.0.1:8000`
