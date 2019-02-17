FROM python:3.7

WORKDIR /opt/gitsu_etl
COPY . /opt/gitsu_etl

ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_etl"

RUN pip install -r requirements_py3.py
