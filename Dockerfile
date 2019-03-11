FROM python:3

ENV SERVERLESS_VERSION=1.37.1
ENV TERRAFORM_VERSION=0.11.10


RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y nodejs
#
#
## === Serverless ===
#
#RUN npm install -g serverless@${SERVERLESS_VERSION} -g
#
## the cache isn't useful anymore?
#RUN rm -rf /root/.cache /root/.npm
#
#
# === Stacker ===

RUN pip install stacker stacker_blueprints


# === Terraform ===

RUN cd /tmp \
 && wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
 && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
 && mv terraform /usr/local/bin \
 && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip


# === Runway ===

WORKDIR /setup

RUN pip install flake8 ply

# if we copy the entire source tree, any change (including to this file)
#  will trigger a complete rebuild
COPY README.rst .
COPY setup.cfg .
COPY setup.py .
COPY runway ./runway
COPY runway.egg-info ./runway.egg-info
COPY scripts ./scripts
COPY tests ./tests

RUN python setup.py install

WORKDIR ..

RUN rm -rf /setup


# ?
ENV PATH=/root/.local/bin/:$PATH

#VOLUME /project
#RUN cd /project

CMD runway

