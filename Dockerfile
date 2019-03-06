FROM python:3

RUN apt-get update && apt-get install -y pandoc

RUN pip3 install flake8 pipenv ply pylint

VOLUME /src

CMD cd /src; bash
