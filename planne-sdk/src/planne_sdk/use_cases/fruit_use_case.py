"""Implementation of fruit-related use cases (CRUD)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlmodel import Session, select

from planne_sdk.models.bucket import Bucket

from ..excpetions import (
    BucketCapacityExceededError,
    BucketNotFoundError,
    FruitOwnerDoesNotMatchBucketOwnerError,
)
from ..models import Fruit, FruitCreate, FruitUpdate
from ._fruit_expiration_handler import (
    expire_fruits_if_needed,
    get_and_expire_fruits_if_needed,
    is_fruit_expired,
)
from .bucket_use_case import _validate_bucket_capacity, get_bucket
from .user_use_case import get_user


def _validate_fruit_bucket_ownership(
    fruit: Fruit, err_msg: str | None = None
) -> None:
    if fruit.bucket and fruit.bucket.user_id != fruit.user_id:
        raise FruitOwnerDoesNotMatchBucketOwnerError(
            err_msg
            or f"Fruit with ID {fruit.id} belongs to a bucket owned by a different user. Change the fruit's owner before adding it to the bucket, or change the bucket's owner to match the fruit's owner."
        )


def create_fruit(*, session: Session, fruit_create: FruitCreate) -> Fruit:
    """Create a new fruit.

    Args:
        session:
            Database session to use for adding and committing the new fruit.
        fruit_create:
            FruitCreate object, containing fruit information.

    Returns:
        The newly created `Fruit` object.

    Raises:
        FruitOwnerDoesNotMatchBucketOwnerError:
            If the fruit belongs to a bucket owned by a different user.
    """
    expires_at = datetime.now(UTC) + timedelta(
        seconds=fruit_create.expiration_seconds
    )

    db_obj = Fruit.model_validate(
        fruit_create,
        update={"expires_at": expires_at},
    )

    _validate_fruit_bucket_ownership(
        db_obj,
        err_msg="Cannot create a fruit belonging to a bucket owned by a different user.",
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_fruit(*, session: Session, fruit_id: UUID | str) -> Fruit | None:
    """Get a fruit by ID.

    Args:
        session:
            Database session to use for the query.
        fruit_id:
            ID of the fruit to retrieve.

    Returns:
        The `Fruit` object if found, or `None` if no fruit with the given
        ID exists.
    """
    if isinstance(fruit_id, str):
        fruit_id = UUID(fruit_id)
    fruits, fruits_not_found = get_and_expire_fruits_if_needed(
        session, [fruit_id]
    )
    if fruits_not_found:
        return None
    return fruits[0] if fruits else None


def get_fruits_by_user(
    *, session: Session, user_id: UUID | str
) -> list[Fruit] | None:
    """Get all fruits for a specific user.

    Args:
        session:
            Database session to use for the query.
        user_id:
            ID of the user whose fruits to retrieve.

    Returns:
        A list of `Fruit` objects belonging to the user. Empty list if no
        fruits exist for the user. None if the user with the given ID does not
        exist.
    """
    if not get_user(session=session, id=user_id):
        return None
    statement = select(Fruit.id).where(Fruit.user_id == user_id)
    fruit_ids = list(session.exec(statement).all())

    fruits, _ = get_and_expire_fruits_if_needed(session, fruit_ids)
    return fruits


def get_fruits_by_bucket(
    *, session: Session, bucket_id: UUID | str
) -> list[Fruit] | None:
    """Get all fruits in a specific bucket.

    Args:
        session:
            Database session to use for the query.
        bucket_id:
            ID of the bucket whose fruits to retrieve.

    Returns:
        A list of `Fruit` objects in the bucket. Empty list if no fruits exist
        in the bucket. None if the bucket with the given ID does not exist.
    """
    # get_bucket() already calls expire_fruits_if_needed() for the bucket's
    # fruits, so there's no need to call it again here
    if not get_bucket(session=session, bucket_id=bucket_id):
        return None
    statement = select(Fruit).where(Fruit.bucket_id == bucket_id)
    return list(session.exec(statement).all())


def update_fruit(
    *, session: Session, db_fruit: Fruit, fruit_in: FruitUpdate
) -> Fruit | None:
    """Update an existing fruit.

    Args:
        session:
            Database session to use for updating and committing the fruit.
        db_fruit:
            The existing fruit object to update.
        fruit_in:
            FruitUpdate object, containing the fields and values to update.

    Returns:
        The updated `Fruit` object.

    Raises:
        FruitOwnerDoesNotMatchBucketOwnerError:
            If the fruit belongs to a bucket owned by a different user.
    """
    # fruit_data = fruit_in.model_dump(exclude_unset=True)
    if fruit_in.expiration_seconds:
        db_fruit.expires_at = db_fruit.created_at + timedelta(
            seconds=fruit_in.expiration_seconds
        )
        if is_fruit_expired(db_fruit):
            session.delete(db_fruit)
            session.commit()
            return None
    if fruit_in.name:
        db_fruit.name = fruit_in.name
    if fruit_in.price:
        db_fruit.price = fruit_in.price
    if db_fruit.bucket_id != fruit_in.bucket_id:
        if fruit_in.bucket_id is not None:
            bucket = get_bucket(session=session, bucket_id=fruit_in.bucket_id)
            if not bucket:
                raise BucketNotFoundError(
                    f"Bucket with ID {fruit_in.bucket_id} does not exist."
                )
            # Refresh in case any of the bucket's existing fruits were expired
            # by get_bucket()
            session.refresh(bucket)
            if len(bucket.fruits) + 1 > bucket.capacity:
                raise BucketCapacityExceededError(
                    f"Cannot add fruit to bucket with ID {fruit_in.bucket_id} because it would exceed the bucket's capacity of {bucket.capacity}."
                )
            db_fruit.bucket = bucket

        db_fruit.bucket_id = fruit_in.bucket_id

    _validate_fruit_bucket_ownership(db_fruit)

    session.add(db_fruit)
    session.commit()
    session.refresh(db_fruit)
    return db_fruit


def delete_fruit(*, session: Session, fruit_id: UUID | str) -> Fruit | None:
    """Delete a fruit by ID.

    Args:
        session:
            Database session to use for the deletion.
        fruit_id:
            ID of the fruit to delete.

    Returns:
        The deleted Fruit object if found and deleted, or `None` if no fruit
        with the given ID was found.
    """
    fruit = session.get(Fruit, fruit_id)
    if not fruit:
        return None
    if is_fruit_expired(fruit):
        return_value = None
    else:
        return_value = fruit

    session.delete(fruit)
    session.commit()
    return return_value
