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
- [PEP 257 docstrings](https://peps.python.org/pep-0257/)



----------

# Getting Started

## Pre-requisites

To run the project locally for testing and validation, you must first install all the pre-requisites below.

- add_here
- add_here
- add_here
- add_here
- add_here
- add_here



## Running The Project

First, clone the repository with the command:

```console
git clone git@github.com:vinivosh/planne-backend-challenge.git
```

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec commodo dolor felis, ac tincidunt elit tristique in. Aliquam accumsan venenatis nisi nec venenatis. Donec odio quam, lacinia a ipsum sit amet, placerat vehicula augue. Suspendisse lobortis, libero eu maximus auctor, erat justo finibus dolor, in convallis arcu dolor ac risus. In hac habitasse platea dictumst. Curabitur eros nunc, volutpat eget tellus id, elementum suscipit dui. Morbi id lacus et nisl congue maximus. Vestibulum et enim et neque ultrices pharetra quis sodales velit. Donec pretium porttitor lacus mollis commodo. Mauris at velit neque.

> Note: if you use [**`mise`** (a.k.a. mise-en-place)](https://mise.jdx.dev/about.html) in your machine, it might be needed to run the command below to let `mise` trust the config file `.mise.toml`. This file just tells `mise` to let `uv` manage the Python version.
> 
> ```console
> mise trust
> ```
>
> Run this in both the `./fruit-full` and the `./planne-sdk` sub-folders.



----------

# Development

Developing for the project requires extra steps besides doing everything in the [Getting Started section](#getting-started).

Install the necessary pre-commit hooks by running the commands below in the root directory of this repository.

```
source ./fruit-full/.venv/bin/activate
pre-commit install
pre-commit install --hook-type commit-msg
```


