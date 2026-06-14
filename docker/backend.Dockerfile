FROM docker:28-cli AS docker_cli

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=docker_cli /usr/local/bin/docker /usr/local/bin/docker

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY certs /app/certs
COPY docker/start-backend.sh /app/docker/start-backend.sh

RUN chmod +x /app/docker/start-backend.sh

EXPOSE 8000

CMD ["/app/docker/start-backend.sh"]
