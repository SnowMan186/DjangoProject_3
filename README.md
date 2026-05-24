# Курсовой проект DRF — Инструкция по запуску и деплою

## Локальный запуск (Docker Compose)
1. Установите Docker и Docker Compose.
2. Склонируйте репозиторий.
3. Создайте `.env` на основе `.env.example`.
4. Запустите проект одной командой:
   ```bash
   docker-compose up -d --build
   ```
5. Проект доступен по адресу http://localhost/
6. Для остановки:
   ```bash
   docker-compose down -v
   ```
7. Для запуска тестов и линтинга локально используйте GitHub Actions или ручные команды из workflow.