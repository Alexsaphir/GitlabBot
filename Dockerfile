ARG PYTHON_FLAVOR=alpine
FROM python:3.12-${PYTHON_FLAVOR} AS build

WORKDIR /opt/GitlabBot
COPY . .
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-${PYTHON_FLAVOR}

LABEL org.opencontainers.image.source="https://github.com/Alexsaphir/GitlabBot"

ENV CONFIG_FILE='.gitlabbot.yaml'

WORKDIR /opt/GitlabBot
COPY --from=build /opt/GitlabBot/dist dist/

RUN apk add curl git kustomize helm

RUN curl -sSL https://github.com/homeport/dyff/releases/download/v1.9.0/dyff_1.9.0_linux_amd64.tar.gz | tar -xz && \
    curl -sSL https://github.com/fluxcd/flux2/releases/download/v2.3.0/flux_2.3.0_linux_amd64.tar.gz | tar -xz && \
    mv dyff /usr/local/bin/  && \
    mv flux /usr/local/bin/

RUN pip install --no-cache-dir $(find dist -name *.whl) && \
    rm -rf dist/
