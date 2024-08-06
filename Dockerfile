FROM python:3.11-alpine as base

LABEL maintainer="conduit"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1

RUN apk add --update --virtual .build-deps \
    build-base \
    postgresql-dev \
    python3-dev \
    libpq

COPY requirements.txt /conduit/requirements.txt
RUN python3 -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools==65.5.1 && \
    /py/bin/pip install -r /conduit/requirements.txt

FROM python:3.11-alpine
RUN apk add libpq
COPY --from=base /py /py
COPY ./conduit /conduit
WORKDIR /conduit
ENV PATH="/py/bin:$PATH"
EXPOSE 8000
