FROM python:3.12-alpine
LABEL authors="alexandre"

ENV CONFIG_FILE='.gitlabbot.yaml'

RUN apk add curl git kustomize helm

RUN curl -sSL https://github.com/homeport/dyff/releases/download/v1.9.0/dyff_1.9.0_linux_amd64.tar.gz | tar -xz && \
    curl -sSL https://github.com/fluxcd/flux2/releases/download/v2.3.0/flux_2.3.0_linux_amd64.tar.gz | tar -xz && \
    mv dyff /usr/local/bin/  && \
    mv flux /usr/local/bin/ \

RUN pip install GitlabBot==0.1.0
