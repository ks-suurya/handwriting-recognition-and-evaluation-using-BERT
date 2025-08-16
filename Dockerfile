version: '3.8'

services:
  # PostgreSQL Database Service
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=htr_db
    networks:
      - htr-network

  # Redis Service for Celery
  redis:
    image: redis:7-alpine
    networks:
      - htr-network

  # Flask Web Application Service
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis
    networks:
      - htr-network
    command: >
      sh -c "flask db upgrade &&
             gunicorn --bind 0.0.0.0:5000 run:app"

  # Celery Worker Service
  worker:
    build: .
    command: celery -A app.tasks.celery worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - redis
      - db
    networks:
      - htr-network

networks:
  htr-network:
    driver: bridge

volumes:
  postgres_data:
