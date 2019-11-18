FROM python:3.7-slim-buster

ENV TERM linx

# Airflow
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG SERVICE_ENVIRONMENT=dev

ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV SERVICE_ENVIRONMENT=${SERVICE_ENVIRONMENT}

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

WORKDIR /opt/gitsu_etl

ENV PYTHONPATH /opt/gitsu_etl


WORKDIR ${AIRFLOW_USER_HOME}

# Add library to PYTHONPATH
RUN pip install -U pip setuptools wheel

# Python Requirements
COPY requirements.txt .

# IF SERVICE_ENVIRONMENT = 'dev'
RUN if [ "${SERVICE_ENVIRONMENT}" = "dev" ]; then \
	pip install -r requirements.txt \
	; fi

COPY requirements_freeze.txt .

# check dev requirements for updates
RUN if [ "${SERVICE_ENVIRONMENT}" = "dev" ]; then \
	pip freeze \
	&& pip freeze > /tmp/updated_requirements_freeze.txt \
	&& diff --strip-trailing-cr /tmp/updated_requirements_freeze.txt requirements_freeze.txt \
	; fi

# IF SERVICE_ENVIRONMENT = 'stage' or 'prod'
RUN if [ "${SERVICE_ENVIRONMENT}" != "dev" ]; then \
	pip install -r requirements_freeze.txt \
	; fi

COPY dags ${AIRFLOW_USER_HOME}/dags

COPY entrypoint.sh /entrypoint.sh

COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

RUN chown -R airflow: ${AIRFLOW_USER_HOME}

EXPOSE 8080 5555 8793

USER airflow
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]
