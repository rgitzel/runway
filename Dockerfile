FROM python:2.7

RUN apt-get update && apt-get install -y pandoc

RUN pip install flake8 pipenv ply pylint

WORKDIR /setup
COPY . .
RUN pipenv sync -d
WORKDIR ..
RUN rm -rf /setup

VOLUME /src

CMD cd /src; bash
