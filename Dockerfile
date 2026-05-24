# --- Этап 1: Сборка зависимостей (для ускорения кэширования) ---
FROM python:3.11-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости (нужны для сборки некоторых питоновских библиотек)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем только файлы зависимостей на первом этапее
COPY requirements.txt .

# Устанавливаем зависимости из PyPI
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# --- Этап 2: Финальный образ (минимальный размер) ---
FROM base AS final

# Копируем весь проект в контейнер
COPY . .

# Собираем статику (для продашена)
RUN python manage.py collectstatic --noinput

# Задаем переменную для Gunicorn
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000"

# Запускаем сервер (Gunicorn)
CMD ["gunicorn", "config.wsgi:application"]