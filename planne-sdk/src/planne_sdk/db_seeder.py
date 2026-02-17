"""Helper functions to seed the database for tests.

Implements a `build(model_class, **kwargs)` function for each model that returns
an instance of that model with default values for all fields, which can be
overridden by passing field values as keyword arguments.

Also implements an `insert(model_class, session, **kwargs)` function to do the same but
also insert the instance into the database.
"""

from datetime import UTC, datetime, timedelta
from random import randint
from typing import Any
from uuid import uuid4

from faker import Faker
from sqlmodel import Session

from planne_sdk.models import Bucket, Fruit, User

DEFAULT_USER_PASSWORD = "@Pass.123Tmp"
DEFAULT_USER_PASSWORD_HASHED = "$argon2id$v=19$m=65536,t=3,p=4$pVRKSal1rjWmdI4RQkjJ2Q$dheWYRWIZWlZfnqcchEXPIYqUyLDwsavvgdLzUYqI48"

DEFAULT_FRUIT_EXPIRATION_TIMEDELTA = timedelta(minutes=5)
DEFAULT_BUCKET_CAPACITY = 10

FAKER_SEED = randint(0, 99999)
FAKER_LOCALE = ["pt_BR", "en_US"]
faker = Faker(locale=FAKER_LOCALE)
faker.seed_instance(FAKER_SEED)


###############################################################################
# Private model-specific build and insert functions
###############################################################################


def _build_user(**kwargs) -> User:
    now = datetime.now(UTC)

    data = {
        "email": kwargs.get(
            "email",
            faker.email(
                domain="mail.com",
            ),
        ),
        "full_name": kwargs.get(
            "full_name", f"{faker.first_name()} {faker.last_name()}"
        ),
        "id": kwargs.get("id", uuid4()),
        "is_superuser": kwargs.get("is_superuser", False),
        "hashed_password": kwargs.get(
            "hashed_password", DEFAULT_USER_PASSWORD_HASHED
        ),
        "buckets": kwargs.get("buckets", []),
        "fruits": kwargs.get("fruits", []),
        "created_at": kwargs.get("created_at", now),
        "updated_at": kwargs.get("updated_at", now),
    }

    return User(**data)


def _build_fruit(**kwargs) -> Fruit:
    now = datetime.now(UTC)

    data = {
        "id": kwargs.get("id", uuid4()),
        "name": kwargs.get("name", faker.word()),
        "price": kwargs.get("price", randint(50, 2000)),
        "bucket": kwargs.get("bucket", None),
        "user": kwargs.get("user", _build_user()),
        "expires_at": kwargs.get(
            "expires_at", now + DEFAULT_FRUIT_EXPIRATION_TIMEDELTA
        ),
        "created_at": kwargs.get("created_at", now),
        "updated_at": kwargs.get("updated_at", now),
    }

    return Fruit(**data)


def _build_bucket(**kwargs) -> Bucket:
    now = datetime.now(UTC)

    data = {
        "capacity": kwargs.get("capacity", DEFAULT_BUCKET_CAPACITY),
        "id": kwargs.get("id", uuid4()),
        "user": kwargs.get("user", _build_user()),
        "fruits": kwargs.get("fruits", []),
        "created_at": kwargs.get("created_at", now),
        "updated_at": kwargs.get("updated_at", now),
    }

    return Bucket(**data)


###############################################################################
# Universal build and insert functions
###############################################################################


def build(model_type_or_name: type | str, **kwargs) -> Any:
    """Build an instance of the given model class with default values.

    Defaults can be overridden by passing field values as keyword arguments.

    Args:
        model_type_or_name:
            Model class or name of the model to build. E.g. `User` or `"user"`.
            Names are case-insensitive.
        **kwargs:
            Field names and values to override the defaults when building the
            model instance.

    Raises:
        RuntimeError:
            If no build function is found for the given model type or name.
    """
    if isinstance(model_type_or_name, str):
        fn_name = f"_build_{model_type_or_name.lower()}"
    else:
        fn_name = f"_build_{model_type_or_name.__name__.lower()}"

    if fn_name in globals():
        return globals()[fn_name](**kwargs)
    raise RuntimeError(
        f"No function `{fn_name}()` found in file `{__file__}`."
    )


def insert(model_type_or_name: type | str, session: Session, **kwargs) -> Any:
    """Insert in DB an instance of the given model with default values.

    Defaults can be overridden by passing field values as keyword arguments.

    Args:
        model_type_or_name:
            Model class or name of the model to insert. E.g. `Bucket` or
            `"bucket"`. Names are case-insensitive.
        session:
            SQLModel session to use for inserting the instance into the
            database.
        **kwargs:
            Field names and values to override the defaults when inserting the
            model instance.

    Raises:
        RuntimeError:
            If no necessary build function is found for the given model type or
            name.
    """
    instance = build(model_type_or_name, **kwargs)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance
