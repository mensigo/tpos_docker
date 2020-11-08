FROM python:3.6-alpine

EXPOSE 5050

WORKDIR /code

COPY requirements.txt /code
RUN pip install -U pip
RUN pip install -r requirements.txt

COPY config.ini /code
COPY load_csv.py /code

CMD python load_csv.py
