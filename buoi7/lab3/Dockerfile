FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY buoi7/lab3/src /app/src
WORKDIR /app/src

EXPOSE 5000

CMD ["sh", "-c", "flask --app ecommerce_api.main:create_app db upgrade && gunicorn --bind 0.0.0.0:5000 --workers 2 'ecommerce_api.main:create_app()'"]
