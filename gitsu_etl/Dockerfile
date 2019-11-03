FROM python:3.7

WORKDIR /opt/gitsu_etl

ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_etl"

RUN pip install -U pip

COPY requirements.txt .
COPY requirements_freeze.txt .

# # IF service_environment = 'dev'
# RUN pip install -r requirements.txt
# RUN pip freeze
# RUN pip freeze > /tmp/updated_requirements_freeze.txt
# RUN diff -c /tmp/updated_requirements_freeze.txt requirements_freeze.txt

# IF service_environment = 'dev' or 'stage'
RUN pip install -r requirements_freeze.txt

COPY . .
