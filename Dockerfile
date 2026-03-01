FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Postgres driver build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

# Static uchun papkalar (settings.py STATIC_ROOT=/app/staticfiles, MEDIA_ROOT=/app/media bo'lsa yaxshi)
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# config.wsgi sizda bor (config/wsgi.py)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]