"""Implementation of bucket-related use cases (CRUD)."""

from uuid import UUID

from sqlmodel import Session, select

from ..excpetions import (
    BucketCapacityExceededError,
    BucketNotEmptyError,
    FruitNotFoundError,
    FruitOwnerDoesNotMatchBucketOwnerError,
    UserNotFoundError,
)
from ..models import Bucket, BucketCreate, BucketUpdate, User
from ._fruit_expiration_handler import (
    expire_fruits_if_needed,
    get_and_expire_fruits_if_needed,
)


def _validate_bucket_fruits_ownership(
    bucket: Bucket, err_msg: str | None = None
) -> None:
    for fruit in bucket.fruits:
        if fruit.user_id != bucket.user_id:
            raise FruitOwnerDoesNotMatchBucketOwnerError(
                err_msg
                or f"Fruit with ID {fruit.id} does not belong to the bucket's owner with ID {bucket.user_id}. Change the fruit's owner before adding it to the bucket, or change the bucket's owner to match the fruit's owner."
            )

def _validate_bucket_capacity(
    bucket: Bucket, new_fruit_qnt: int = 0, err_msg: str | None = None
) -> None:
    if len(bucket.fruits) > bucket.capacity + new_fruit_qnt:
        raise BucketCapacityExceededError(
            err_msg
            or f"Bucket capacity of {bucket.capacity} exceeded. Cannot save this bucket with {len(bucket.fruits)} fruits. Remove some fruits or increase the bucket's capacity."
        )


def create_bucket(*, session: Session, bucket: BucketCreate) -> Bucket:
    """Create a new bucket.

    Args:
        session:
            Database session to use for adding and committing the new Bucket.
        bucket:
            Bucket object, containing bucket information.

    Returns:
        The newly created `Bucket` object.

    Raises:
        FruitNotFoundError:
            If any fruit in the bucket does not exist (or has expired already).
        FruitOwnerDoesNotMatchBucketOwnerError:
            If any fruit in the bucket does not belong to the bucket's owner.
    """
    fruits_to_add = []
    if bucket.fruits:
        fruits_to_add, fruits_not_found = get_and_expire_fruits_if_needed(
            session, bucket.fruits
        )
        if fruits_not_found:
            raise FruitNotFoundError(
                f"Some Fruits were not found. Cannot create bucket with non-existent fruits: {fruits_not_found}"
            )

    new_bucket = Bucket.model_validate(
        bucket, update={"fruits": fruits_to_add}
    )
    _validate_bucket_capacity(new_bucket)
    _validate_bucket_fruits_ownership(new_bucket)
    session.add(new_bucket)
    session.commit()
    session.refresh(new_bucket)
    return new_bucket


def get_bucket(*, session: Session, bucket_id: UUID | str) -> Bucket | None:
    """Get a bucket by ID.

    Args:
        session:
            Database session to use for the query.
        bucket_id:
            ID of the bucket to retrieve.

    Returns:
        The `Bucket` object if found, or `None` if no bucket with the given
        ID exists.
    """
    bucket = session.get(Bucket, bucket_id)
    if bucket is None:
        return None

    expire_fruits_if_needed(session, bucket.fruits)
    session.refresh(bucket)
    return bucket


def get_buckets_by_user(
    *, session: Session, user_id: UUID | str
) -> list[Bucket]:
    """Get all buckets for a specific user.

    Args:
        session:
            Database session to use for the query.
        user_id:
            ID of the user whose buckets to retrieve.

    Returns:
        A list of `Bucket` objects belonging to the user. Empty list if no
        buckets exist for the user.
    """
    statement = select(Bucket).where(Bucket.user_id == user_id)
    buckets = list(session.exec(statement).all())

    for bucket in buckets:
        expire_fruits_if_needed(session, bucket.fruits)
        session.refresh(bucket)
    return buckets


def update_bucket(
    *, session: Session, db_bucket: Bucket, bucket_in: BucketUpdate
) -> Bucket:
    """Update an existing bucket. Partial updates supported.

    Args:
        session:
            Database session to use for updating and committing the bucket.
        db_bucket:
            The existing bucket object to update.
        bucket_in:
            BucketUpdate object, containing the fields and values to update.

    Returns:
        The updated `Bucket` object.

    Raises:
        FruitNotFoundError:
            If any fruit in the updated bucket does not exist (or has expired
            already).
        FruitOwnerDoesNotMatchBucketOwnerError:
            If any fruit in the updated bucket does not belong to the bucket's
            owner.
    """
    expire_fruits_if_needed(session, db_bucket.fruits)
    session.refresh(db_bucket)

    if bucket_in.fruits:
        fruits_to_update, fruits_not_found = get_and_expire_fruits_if_needed(
            session, bucket_in.fruits
        )
        if fruits_not_found:
            raise FruitNotFoundError(
                f"Some Fruits were not found. Cannot update bucket with non-existent fruits: {fruits_not_found}"
            )

        db_bucket.fruits = fruits_to_update

    if bucket_in.user_id:
        new_user = session.get(User, bucket_in.user_id)
        if new_user is None:
            raise UserNotFoundError(
                f"User with ID {bucket_in.user_id} does not exist. Cannot update bucket with non-existent user as owner."
            )
        db_bucket.user = new_user
        db_bucket.user_id = new_user.id

    if bucket_in.capacity:
        db_bucket.capacity = bucket_in.capacity

    _validate_bucket_capacity(db_bucket)
    _validate_bucket_fruits_ownership(db_bucket)

    session.add(db_bucket)
    session.commit()
    session.refresh(db_bucket)
    return db_bucket


def delete_bucket(*, session: Session, bucket_id: UUID | str) -> Bucket | None:
    """Delete a bucket by ID.

    Args:
        session:
            Database session to use for the deletion.
        bucket_id:
            ID of the bucket to delete.

    Returns:
        The deleted bucket if it was successfully deleted, `None` if no bucket
        with the given ID was found.

    Raises:
        BucketNotEmptyError:
            If the bucket still contains fruits.
    """
    bucket = session.get(Bucket, bucket_id)
    if not bucket:
        return None

    expire_fruits_if_needed(session, bucket.fruits)
    session.refresh(bucket)

    if len(bucket.fruits) > 0:
        raise BucketNotEmptyError()

    session.delete(bucket)
    session.commit()
    return bucket
