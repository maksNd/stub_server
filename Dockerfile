# Используем Python
FROM python:3.12-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Копируем проект
WORKDIR /app
COPY . /app

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем конфиг Nginx
RUN rm /etc/nginx/nginx.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Expose порты
EXPOSE 80

# Команда запуска: uvicorn и nginx одновременно
CMD bash -c "python -m uvicorn app:app --host 127.0.0.1 --port 7777 & nginx -g 'daemon off;'"
