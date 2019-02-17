# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-datascience-notebook
FROM jupyter/scipy-notebook:latest

WORKDIR /opt/gitsu_analytics
COPY . /opt/gitsu_analytics

# Add library to PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/opt/gitsu_analytics"

# Juptyer Extensions
RUN jupyter labextension install @jupyterlab/toc
RUN jupyter labextension install jupyterlab-drawio

# Notebooks Entry Directory
WORKDIR /opt/gitsu_analytics/notebooks
EXPOSE 8888
