FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED 1

WORKDIR "/app"

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && apt-get autoremove

COPY requirements.txt ./
RUN python -m pip --disable-pip-version-check --no-cache-dir install -r requirements.txt \
    && rm -rf requirements.txt

COPY ["setup.py", "README.md", "requirements.txt", "./pkg/"]
COPY MFramework ./pkg/MFramework
RUN python -m pip --disable-pip-version-check --no-cache-dir install ./pkg \
    && rm -rf ./pkg

VOLUME ["/app/data", "/app/bot", "/app/extenstions", "/app/locale"]

ENTRYPOINT [ "python", "-m", "MFramework", "bot", "--cfg=data/secrets.ini", "--log=DEBUG" ]

FROM base as dev

ENV DEV 1
ENV PYTHONPATH "${PYTHONPATH}:/modules"

VOLUME ["/modules"]
