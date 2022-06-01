FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/modules"

WORKDIR "/app"

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && apt-get autoremove

COPY requirements.txt ./
RUN python -m pip --disable-pip-version-check --no-cache-dir install -r requirements.txt \ 
    && rm -rf requirements.txt \
    && sed -i -e 's/_init_params,/_init_params + ["**kwargs"],/g' /usr/local/lib/python3.10/dataclasses.py

COPY ["setup.py", "README.md", "requirements.txt", "./pkg/"]
COPY MFramework ./pkg/MFramework
RUN python -m pip --disable-pip-version-check --no-cache-dir install ./pkg \
    && rm -rf ./pkg

COPY .docker/docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

VOLUME ["/app/data", "/app/bot", "/app/extenstions", "/app/locale"]

ENTRYPOINT [ "python", "-m", "MFramework", "bot", "--cfg=data/secrets.ini", "--log=DEBUG" ]
#ENTRYPOINT ["./docker-entrypoint.sh", "--log=INFO"]

FROM base as dev

VOLUME ["/modules"]

ENV DEV 1

COPY get_repos.py ./
ENTRYPOINT ["./docker-entrypoint.sh", "--log=DEBUG"]
