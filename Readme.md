# Coffee App Backend

## Context
This repository is part of the coffee rating application project. The project
provides a rating appliation for coffees where its possible to add/delete and
rate different coffee beans. The project consists of the following repositories:
- [Frontend](https://github.com/andifg/coffee_frontend_ts.git) - A react typescript progressive web app
- [Backend](https://github.com/andifg/coffee_backend.git) - Fastapi based python backend
- [Resizer](https://github.com/andifg/coffee_image_resizer.git) - Python based image resizer listening on kafka messages
- [Helm Chart](https://github.com/andifg/coffee-app-chart.git) - Helm Chart deploying front and backend together with database and minio hem charts
- [GitOps](https://github.com/andifg/coffee-app-gitops.git) - Gitops repository for ArgoCD reflecting deployed applications for test and prod env

## Prerequesits

- Install pre-commit hocks and install them via
```bash
pre-commit install
```

- [Install poetry](https://python-poetry.org/)

## Test
```bash
poetry run ./scripts/test.sh
```

## Format & Lint
```bash
poetry run ./scripts/format.sh
```

## Run locally without container
```bash
poetry run python3 -m coffee_backend
```

## Build locally
```bash
docker build -t coffee_backend:v1 -f ./Containerfile .
```

## Run locally with container
- Build container first

```bash
docker run -it -p 9000:8000  --name coffee_backend coffee_backend:v1
```

## Local End To End Dev & Test Environment

In order to execute local end to end test for the coffee app its possible to
start the docker-compose inside the devservice directory. It will spin up an
environment with frontend, backend, resizer as well as all dependent systems.
In order to work properly the hostname "keycloak" must resolve to localhost.
The following environment variables need to be defined to point to the local
directories of the repositories:
FRONTEND_PATH=<aboslut path of frontend git repository>
BACKEND_PATH=<absolut path of backend git repository>
RESIZER_PATH=<absolut path of resizer git respository>