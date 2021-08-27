FROM python:3.8-slim-buster

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP app.py

CMD gunicorn --bind 0.0.0.0:$PORT wsgi