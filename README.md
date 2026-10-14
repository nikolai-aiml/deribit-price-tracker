# Deribit Price Tracker

Сервис для периодического получения индексных цен BTC и ETH с криптобиржи Deribit, сохранения истории в PostgreSQL и предоставления данных через REST API на FastAPI.

## Возможности

* Получение индексных цен `btc_usd` и `eth_usd` через публичный API Deribit.
* Автоматический сбор цен каждую минуту с помощью Celery Beat.
* Выполнение фоновых задач с помощью Celery Worker.
* Хранение истории цен в PostgreSQL.
* Получение истории, последней цены и цен за указанную дату через HTTP GET.
* Автоматическое документирование API через Swagger UI.
* Запуск сервисов в Docker Compose.

## Технологии

* Python 3.11+
* FastAPI
* SQLAlchemy
* PostgreSQL 16
* Celery
* Redis 7
* aiohttp
* Docker Compose
* pytest и Ruff

## Архитектура

```text
Deribit public API
        |
        v
  DeribitClient
        |
        v
  PriceService
        |
        v
 PriceRepository
        |
        v
    PostgreSQL

Celery Beat --> Redis --> Celery Worker
                              |
                              v
                       PriceService

HTTP Client --> FastAPI --> PriceService
                            |
                            v
                      PriceRepository
```

### Структура проекта

```text
app/
  api/routes/prices.py       # HTTP endpoints
  clients/deribit.py         # Клиент Deribit
  core/config.py             # Конфигурация приложения
  db/base.py                 # SQLAlchemy Base
  db/models.py               # Модель PriceHistory
  db/session.py              # Подключение к PostgreSQL
  repositories/
    price_repository.py      # Работа с запросами к БД
  schemas/price.py            # Схема ответа API
  services/price_service.py  # Бизнес-логика
  tasks/
    celery_app.py            # Настройка Celery Beat
    collect_prices.py        # Фоновая задача
  main.py                    # FastAPI application

tests/
  test_prices_api.py         # Тесты API

compose.yaml
Dockerfile
pyproject.toml
.env.example
```

## Требования

Для запуска необходимы Docker Desktop с Docker Compose и Git.

Для локального запуска Python-кода без Docker потребуется Python 3.11 или новее.

## Запуск через Docker Compose

### 1. Клонирование проекта

```bash
git clone <GITLAB_REPOSITORY_URL>
cd deribit-price-tracker
```

Замените `<GITLAB_REPOSITORY_URL>` адресом своего репозитория.

### 2. Настройка окружения

Создайте `.env` на основе шаблона:

В PowerShell:

```powershell
Copy-Item .env.example .env
```

При необходимости измените `POSTGRES_PASSWORD` на надёжный пароль и используйте его в `DATABASE_URL`.

Не публикуйте `.env` в Git.

### 3. Запуск сервисов

```bash
docker compose up --build -d
```

Проверить состояние контейнеров:

```bash
docker compose ps
```

Посмотреть логи:

```bash
docker compose logs -f api worker beat
```

### 4. Проверка API

Swagger UI:

http://localhost:8000/docs

Проверка работоспособности:

http://localhost:8000/health

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

### 5. Проверка PostgreSQL

```bash
docker compose exec db psql -U prices_user -d prices
```

Запрос для просмотра последних цен:

```sql
SELECT id, ticker, price, timestamp
FROM price_history
ORDER BY timestamp DESC
LIMIT 10;
```

### 6. Остановка

```bash
docker compose down
```

Чтобы удалить также данные PostgreSQL, сохранённые в Docker volume, используй команду:

```bash
docker compose down -v
```

**Внимание:** команда `down -v` удаляет сохранённые данные базы.

## API

Все эндпоинты используют HTTP GET и требуют query-параметр `ticker`.

Поддерживаемые значения: `btc_usd`, `eth_usd`.

### Получить всю историю цен

```http
GET /api/v1/prices?ticker=btc_usd
```

Возвращает список сохранённых записей указанного тикера в порядке убывания времени.

### Получить последнюю цену

```http
GET /api/v1/prices/latest?ticker=btc_usd
```

Возвращает последнюю запись для тикера.

Если данные отсутствуют, возвращается HTTP 404.

### Получить цены за дату

```http
GET /api/v1/prices/by-date?ticker=btc_usd&date=2026-10-14
```

Параметры:

* `ticker` — обязательный тикер: `btc_usd` или `eth_usd`.
* `date` — дата в формате `YYYY-MM-DD`.

Фильтрация выполняется по календарному дню UTC. Возвращается список записей за этот день в порядке возрастания времени.

### Формат ответа

```json
{
  "id": 10,
  "ticker": "btc_usd",
  "price": "82616.15000000",
  "timestamp": 1791983220009
}
```

`timestamp` хранится в UNIX timestamp в миллисекундах. Цена передаётся как десятичное число, сериализованное в JSON строкой для сохранения точности.

### Коды ответов

* `200 OK` — запрос выполнен.
* `404 Not Found` — отсутствует последняя цена для запрошенного тикера.
* `422 Unprocessable Entity` — отсутствует обязательный параметр или переданы некорректные значения.

## Тестирование

Установить проект с зависимостями для разработки:

```bash
python -m pip install -e ".[dev]"
```

Запустить тесты:

```bash
python -m pytest -v
```

Проверить стиль кода:

```bash
ruff check app tests
```

Тесты API используют подмену бизнес-логики и не требуют обращения к реальной бирже.

## Design decisions

### PostgreSQL

PostgreSQL выбран как надёжная реляционная база данных для хранения исторических котировок. Таблица `price_history` содержит тикер, цену и время получения данных.

### SQLAlchemy и Repository

SQLAlchemy отвечает за взаимодействие с базой данных. Репозиторий `PriceRepository` инкапсулирует запросы и операции сохранения, а `PriceService` координирует бизнес-логику.

Такое разделение упрощает тестирование и уменьшает связанность компонентов.

### Celery и Redis

Celery используется для выполнения периодической задачи в отдельном процессе. Celery Beat планирует запуск каждую минуту, Redis служит брокером сообщений, а Worker выполняет сбор и сохранение цен.

Это позволяет не привязывать сбор данных к жизненному циклу HTTP-запросов.

### aiohttp

Асинхронный HTTP-клиент используется для запросов к Deribit. Это позволяет выполнять сетевые операции без блокировки event loop во время ожидания ответа.

### UNIX timestamp в миллисекундах

Время хранится как UNIX timestamp в миллисекундах, что соответствует формату временной метки Deribit. Для выборки по дате границы календарного дня вычисляются в UTC.

### Точность цены

Для цены используется `NUMERIC(20, 8)`, а не тип с плавающей точкой. Это позволяет сохранять десятичную точность финансовых данных.

### Docker Compose

PostgreSQL, Redis, API, Celery Worker и Celery Beat запускаются как отдельные сервисы. Такой подход упрощает локальное развёртывание и делает инфраструктуру воспроизводимой.

## Ограничения и дальнейшее развитие

* Добавить отдельные unit-тесты репозитория и сервиса.
* Рассмотреть идемпотентность фоновой задачи, чтобы повторные попытки не создавали нежелательные дубликаты.
* Добавить миграции схемы БД через Alembic.
* Ограничить объём ответа эндпоинта истории с помощью пагинации.
* Настроить более подробные проверки доступности PostgreSQL и Deribit.
