FROM puckel/docker-airflow:1.10.9

# AIRFLOW_HOME=/usr/local/airflow

# ############################################################################ #
# ETL Scripts Requirements
# ############################################################################ #
ENV APP_HOME "/usr/local/etl"

ENV PATH "${APP_HOME}/bin:$PATH"
ENV AIRFLOW__CORE__DAGS_FOLDER "${APP_HOME}/dags"
ENV PYTHONPATH "${AIRFLOW__CORE__DAGS_FOLDER}:${PATH}"

WORKDIR $APP_HOME

COPY bin/. bin
COPY requirements.txt .
RUN pip_install_requirements.sh requirements.txt

COPY . .

WORKDIR $AIRFLOW_HOME
