FROM python:3.7

# use locked dependencies or allow them to update
ARG requirements_lock=true

WORKDIR /opt/gitsu_etl
COPY . /opt/gitsu_etl

ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_etl"

RUN pip install -U pip
RUN \
 if [ "$requirements_lock" = "true" ] ;\
 then pip install -r requirements_lock.txt ;\
 else pip install -r requirements_txt ;\
 fi
RUN pip freeze
