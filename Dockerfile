FROM python:3.11.1-slim

WORKDIR /app
COPY requirements.txt /app/

RUN pip install -U pip && pip install -r requirements.txt && \
    RUN python manage.py collectstatic --noinput

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "freeWords.wsgi:application"]
