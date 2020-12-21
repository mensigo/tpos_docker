FROM python:3.6-alpine

EXPOSE 5000

WORKDIR /code

COPY requirements.txt /code
RUN pip install -U pip
RUN pip install -r requirements.txt
#RUN apk add bash

COPY config.ini /code
COPY app.py /code
#COPY script.sh /code

#CMD script.sh csv_load
CMD python app.py
