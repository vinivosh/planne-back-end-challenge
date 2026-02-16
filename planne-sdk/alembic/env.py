"""Configuration file for Alembic."""

# ruff: noqa: E402

import os
import sys
from logging.config import fileConfig
from pathlib import Path

import dotenv
from sqlalchemy import engine_from_config, pool

# Add planne-sdk root to the Python path
_FILE_DIR = Path(__file__).parent.resolve()
_PROJECT_DIR = _FILE_DIR.parent.resolve()
sys.path.append(str(_PROJECT_DIR))

import planne_sdk.constants as c
from alembic import context
from planne_sdk.models import (
    SQLModel,  # pyright: ignore[reportPrivateImportUsage]
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# Printing some info on the DB we're connecting
ENV_FILE_PATH = _PROJECT_DIR.joinpath(".env")
loaded_env_vars = dotenv.load_dotenv(ENV_FILE_PATH)

print(f'Alembic | Loaded env vars from "{ENV_FILE_PATH}"? {loaded_env_vars}')
print(f"Alembic | POSTGRES_SERVER={c.POSTGRES_SERVER}")
print(f"Alembic | POSTGRES_PORT={c.POSTGRES_PORT}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = c.get_postgres_uri()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    url = c.get_postgres_uri()

    # Create configuration for the engine
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
