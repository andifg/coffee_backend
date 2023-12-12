# Coffee App Backend

## Context
This repository is part of the coffee rating application project. The project
provides a rating appliation for coffees where its possible to add/delete and
rate different coffee beans. The project consists of the following repositories:
- [Frontend](https://github.com/andifg/coffee_frontend_ts.git) - A react typescript progressive web app
- [Backend](https://github.com/andifg/coffee_backend.git) - Fastapi based python backend
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

## Devservices

In Order to do a full end to end test locally you can start the compose files
inside the [devservices](devservices) directory to launch dependent services that are not
spawn up during the pytest execution (these services can be run executing the
compose file inside the [tests](tests) directory)
Currently available devservices:
- Keycloak



## TODOs:
- Include pagination in coffee read endpoint
- Remove the db_session depens from API Layer to Service layer
- Include responses in the api endpoints to document error message styles