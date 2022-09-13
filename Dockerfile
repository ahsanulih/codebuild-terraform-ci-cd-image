FROM ubuntu:focal
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    git \
    jq \
    unzip \
    wget \
    zip \
    locales \
    openssh-client && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/* && \
    apt-get clean && \
    apt-get autoremove --purge
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
RUN git clone -b v2.2.2 https://github.com/tfutils/tfenv.git ~/.tfenv && \
    ln -s ~/.tfenv/bin/* /usr/local/bin
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools && \
    python3 -m pip install --no-cache-dir --upgrade awscli && \
    python3 -m pip install --no-cache-dir boto3 && \
    python3 -m pip install --no-cache-dir cryptography && \
    python3 -m pip install --no-cache-dir PyJWT && \
    python3 -m pip install --no-cache-dir requests && \
    python3 -m pip install --no-cache-dir Jinja2 && \
    python3 -m pip install --no-cache-dir pandas && \
    python3 -m pip install --no-cache-dir tabulate && \
    python3 -m pip cache purge
RUN tfenv install 0.11.15 &&\
    tfenv install 0.12.31 &&\
    tfenv install 0.13.7 &&\
    tfenv install 1.0.3 &&\
    tfenv use 0.11.15

# https://www.docker.com/blog/docker-can-now-run-within-docker/
VOLUME /var/lib/docker

COPY scripts/ /usr/local/bin/
COPY scripts_infracost/ /usr/local/bin/
