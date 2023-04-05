FROM continuumio/miniconda3

ARG conda_env=fmu_simulator_docker

ADD html_charts ./
ADD fmu_simulation ./
ENV FLASK_APP=main_server.py
ENV FLASK_RUN_HOST=0.0.0.0
#koennen wir aendern wenn alles rennt
#ENV FLASK_ENV=development

COPY environment.yml ./
#RUN conda update -n base -c defaults conda
RUN conda env create -f environment.yml

ENV PATH /opt/conda/envs/$conda_env/bin:$PATH
ENV CONDA_DEFAULT_ENV $conda_env
RUN pip install --upgrade flask_socketio==4.3.1
RUN pip install --upgrade flask_executor==0.10.0
COPY . .

CMD [ "flask", "run" ]