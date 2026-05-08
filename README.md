# LMS Project - Инструкция по запуску (Docker)

## Требования
*   Установить [Docker Engine](https://docs.docker.com/engine/install/)
*   Установить [Docker Compose](https://docs.docker.com/compose/install/) (обычно идет в комплекте)
*   Установить [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/) для сборки образов

## Запуск проекта

1.  **Сборка образов и запуск контейнеров**
    Эта команда соберет образы и запустит все сервисы (БД, Redis, Django, Celery).
    ```bash
    docker compose up --build -d
    ```
2.  **Применение миграций (если не применились автоматически)**
    Если вы изменили модели, выполните:
    ```bash
    docker compose exec web python manage.py makemigrations
    docker compose exec web python manage.py migrate
    ```
3.  **Создание суперпользователя**
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```
4.  **Запуск Celery Worker (если упал)**
    ```bash
    docker compose restart worker beat # Или up -d worker beat если не в режиме -d
    ```
5.  **Остановка проекта**
    ```bash
    docker compose down -v # Флаг -v удалит данные БД! Для сохранения данных используйте без флага.
    ```
6.  **Просмотр логов**
   ```bash
   docker compose logs -f web # Логи веб-сервера
   docker compose logs -f worker # Логи Celery Worker-а
   ```