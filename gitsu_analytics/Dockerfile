# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-datascience-notebook
FROM jupyter/scipy-notebook:latest

# use locked dependencies or allow them to update
ARG requirements_lock=true

WORKDIR /opt/gitsu_analytics
COPY . /opt/gitsu_analytics

# Add library to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_analytics"

# Juptyer Extensions
RUN jupyter labextension install @jupyterlab/toc
RUN jupyter labextension install jupyterlab-drawio

# Python Requirements
RUN pip install -U pip
RUN \
 if [ "$requirements_lock" = "true" ] ;\
 then pip install -r requirements_lock.txt ;\
 else pip install -r requirements_txt ;\
 fi
RUN pip freeze

# Notebooks Entry Directory
WORKDIR /opt/gitsu_analytics/notebooks
EXPOSE 8888
