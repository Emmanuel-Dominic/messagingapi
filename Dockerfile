FROM python:3
LABEL maintainer="Emmanuel Dominic <ematembu2@gmail.com>"
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD sh init.sh && python3 manage.py runserver 0.0.0.0:8000 --settings=config.settings.production
