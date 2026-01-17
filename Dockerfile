FROM python:3.11-slim

WORKDIR /app

COPY backend/ /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --config gunicorn.conf.py
