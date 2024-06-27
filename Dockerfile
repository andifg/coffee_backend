FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4 as base

RUN microdnf install python3.11 -y && /bin/python3.11 -m ensurepip --upgrade && \
    pip3 install --upgrade pip && pip3 install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY ./pyproject.toml /app/

RUN poetry install --without dev --no-root

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4

RUN microdnf install python3.11 -y

COPY --from=base /app/.venv /app/.venv

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY ./coffee_backend ./coffee_backend

ENTRYPOINT ["python", "-m", "coffee_backend"]
