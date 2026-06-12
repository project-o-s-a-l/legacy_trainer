FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin checker

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pytest ruff \
    && python -m pytest --version \
    && python -m ruff --version

WORKDIR /workspace

COPY legacy_checker /opt/legacy_checker
ENV PYTHONPATH=/opt

USER 10001:10001

ENTRYPOINT ["python", "-m", "legacy_checker.run"]
