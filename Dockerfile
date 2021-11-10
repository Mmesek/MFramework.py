FROM python:3.10-slim

ENV PYTHONPATH "${PYTHONPATH}:/modules"
ENV PYTHONPATH "${PYTHONPATH}:/repos"
VOLUME ["/app/data", "/app/bot", "/modules", "/repos", "/app/extenstions", "/app/locale"]
WORKDIR "/app"

COPY requirements.txt ./
RUN python -m pip install --upgrade --no-cache-dir pip && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    sed -i -e 's/_init_params,/_init_params + ["**kwargs"],/g' /usr/local/lib/python3.10/dataclasses.py

COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh", "--log=INFO"]
