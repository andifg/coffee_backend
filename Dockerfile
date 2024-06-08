FROM python:3.12.4 as base

ARG POETRY_VERSION=1.3.2

RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY ./pyproject.toml /app/

RUN poetry config virtualenvs.create false

RUN poetry install --without dev

FROM python:3.12.4

COPY --from=base /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

WORKDIR /app

COPY ./coffee_backend ./coffee_backend

ENTRYPOINT ["python", "-m", "coffee_backend"]
