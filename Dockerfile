FROM python:3.10.2-slim-bullseye

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY . /app

RUN pip install -r requirements.txt
RUN pip install postgres gunicorn
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD gunicorn --bind 0.0.0.0:8000 --workers=3 team.wsgi