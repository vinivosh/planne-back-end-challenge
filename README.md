# Planne Back-end Challenge

My solution to the challenge for a back-end developer position at [Planne](https://www.linkedin.com/company/plannesoftware/). Definitions available in the file [Desafio Backend - Planne.pdf](./Desafio%20Backend%20-%20Planne.pdf).





## Technologies Used

- [Python](https://www.python.org/) language
- [FastAPI](https://fastapi.tiangolo.com/) back-end framework
- [Postgres](https://www.postgresql.org/) database
- [SQL Model](https://sqlmodel.tiangolo.com/) for the ORM
- DB migrations managed by [Alembic](https://alembic.sqlalchemy.org)
- Unit and integration tests with [pytest](https://docs.pytest.org/)
- Containerization with [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)


## Standards followed

- [Semantic Versioning](https://semver.org/#semantic-versioning-200)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary), enforced with the [pre-commit](https://pre-commit.com/#plugins) hook [`commitlint`](https://github.com/opensource-nepal/commitlint?tab=readme-ov-file#pre-commit)
- [PEP8 code style](https://peps.python.org/pep-0008/), enforced with the [`ruff` linter](https://docs.astral.sh/ruff/)
- [Google style docstrings](https://google.github.io/styleguide/pyguide.html#381-docstrings), also enforced with `ruff`



----------

# Getting Started

## Pre-requisites

To run the project locally for testing and validation, you must first install all the pre-requisites below.

- [Git](https://git-scm.com/install/)
- [Python 3.12.x](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv)
- [Docker](https://docs.docker.com/engine/install/)



## Running The Project

First, clone the repository with the command:

```console
git clone git@github.com:vinivosh/planne-backend-challenge.git
```

> Note: if you use [**`mise`** (a.k.a. mise-en-place)](https://mise.jdx.dev/about.html) in your machine, it might be needed to run the command below to let `mise` trust the config file `.mise.toml`. This file just tells `mise` to let `uv` manage the Python version.
> 
> ```console
> mise trust
> ```
>
> Run this in both the `./fruit-full` and the `./planne-sdk` sub-folders.

Create a valid `.env` file at the root of the repository folder, with all required variables defined. Refer to the `.env-sample` file for more information. The same must be done for each one of the projects in this repo, fruit-full and planne-sdk.


### Starting the FruitFULL back-end server + postgres DB

After installing all the requirements and setting up the `.env` file, start the back-end server plus the Postgres DB by simply running the command below from the root folder of the repository:

```console
sudo docker compose up --build
```

On first start the database will get created with the credentials provided by the environment variables.

After a successful start for both the backend and postgers services, you must apply the Alembic migrations to auto-create all tables and fields in the database, by running the command below from anywhere:

```console
sudo docker exec -it fruit_full bash -c 'cd /planne-sdk && POSTGRES_SERVER="planne_db" alembic upgrade head'
```

This will run Alembic inside the back-end docker container, auto-creating everything needed in the DB.

> Note: the name of the container, `fruit_full`, might be different in your machine. Check the correct name with the command: `sudo docker ps`

After this, stop and restart the docker compose by pressing `ctrl` + `c` and then running the first command again.

Now a first superuser should be created successfully, according to the the environment variables, and you are ready to authenticate yourself and test all routes by visiting [localhost:8000/docs](http://localhost:8000/docs) in your machine.



----------

# Development

Developing for the project requires extra steps besides doing everything in the [Getting Started section](#getting-started).

Install the necessary pre-commit hooks by running the commands below in the root directory of this repository.

```
source ./fruit-full/.venv/bin/activate
pre-commit install
pre-commit install --hook-type commit-msg
```


