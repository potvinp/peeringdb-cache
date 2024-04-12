FROM python:3.11.4-slim-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install peeringdb django django-peeringdb

COPY project/. /app/

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
