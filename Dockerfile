FROM python:3.10-slim as base

VOLUME ["/app/data", "/app/bot", "/app/extenstions", "/app/locale"]
WORKDIR "/app"

RUN apt-get update && \
    apt-get install git -y && \
    apt-get clean && \
    apt-get autoremove

COPY requirements.txt ./
RUN python -m pip install --upgrade --no-cache-dir pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    sed -i -e 's/_init_params,/_init_params + ["**kwargs"],/g' /usr/local/lib/python3.10/dataclasses.py

COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh", "--log=INFO"]

FROM base as dev

VOLUME ["/modules"]

ENV PYTHONPATH "${PYTHONPATH}:/modules"
ENV DEV 1

COPY get_repos.py ./
ENTRYPOINT ["./docker-entrypoint.sh", "--log=DEBUG"]
