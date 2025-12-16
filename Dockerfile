# Багатоетапна збірка для оптимізації розміру образу
FROM python:3.11-slim AS builder

WORKDIR /app

# Встановлюємо системні залежності для компіляції
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файли залежностей
COPY requirements.txt .

# Встановлюємо залежності у користувацьку директорію
RUN pip install --no-cache-dir --user -r requirements.txt

# Фінальний етап з легким Alpine образом
FROM python:3.11-alpine

WORKDIR /app

# Встановлюємо wget для health check
RUN apk add --no-cache wget

# Копіюємо встановлені пакети з етапу збірки
COPY --from=builder /root/.local /root/.local

# Додаємо встановлені пакети до PATH
ENV PATH=/root/.local/bin:$PATH

# Створюємо директорію для бази даних з правильними правами
RUN mkdir -p /app/instance /app/data && \
    chmod 755 /app/instance /app/data

# Копіюємо код застосунку
COPY . .

# Налаштування змінних середовища
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/instance/brainrush.db

# Відкриваємо порт
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/ || exit 1

# Команда запуску
CMD ["python", "run.py"]