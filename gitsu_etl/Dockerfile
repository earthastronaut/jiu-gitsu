FROM python:3.7

# use locked dependencies or allow them to update
ARG requirements_lock=true

WORKDIR /opt/gitsu_etl
COPY . /opt/gitsu_etl

ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_etl"

RUN pip install -U pip
RUN \
 if [ "x$requirements_lock" = "true" ] ;\
 then pip install -r requirements_py3_locked.txt ;\
 else pip install -r requirements_py3.txt ;\
 fi
RUN pip freeze | tee -a /opt/freeze_requirements_py3.txt
