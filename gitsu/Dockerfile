FROM python:3.7

WORKDIR /opt/gitsu
COPY . /opt/gitsu
ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu"

RUN pip install -r requirements_py3.py
