FROM python:3.8-slim-buster

# ############################################################################ #
# Environment
# ############################################################################ #

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive

ENV APP_PATH "/usr/src/app"

ENV PATH "${APP_PATH}/bin:$PATH"

ENV PYTHONPATH "${APP_PATH}/packages:$PYTHONPATH"

# Prefect
# "We highly recommend turning off Dask work stealing" 
# https://docs.prefect.io/core/advanced_tutorials/dask-cluster.html
# ENV DASK_DISTRIBUTED__SCHEDULER__WORK_STEALING "False" # case sensitive

# ############################################################################ #
# System Libraries  
# ############################################################################ #

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y \
	libssl-dev \
	libpq-dev \
	python3-dev \
	gcc \
	graphviz \
	libyaml-dev	

# libssl-dev \ openssl libraries for secure connections
# libpq-dev \ postgres libraries
# python3-dev \ required by psutil and other python packages
# gcc \ required by psutil and other python packages for updated headers
# graphviz \ for visualizing prefect flows
# libyaml-dev \ recommended by watchdog python utility https://github.com/gorakhargosh/watchdog

# ############################################################################ #
# Application 
# ############################################################################ #

WORKDIR $APP_PATH

COPY bin/. bin
COPY requirements.txt .
RUN pip_install_requirements.sh requirements.txt

COPY . .

CMD "prefect agent start"
