"""Implementation of bucket-related use cases (CRUD)."""

from uuid import UUID

from sqlmodel import Session, select

from ..excpetions import (
    BucketNotEmptyError,
    FruitOwnerDoesNotMatchBucketOwnerError,
)
from ..models import Bucket, BucketUpdate


def create_bucket(*, session: Session, bucket: Bucket) -> Bucket:
    """Create a new bucket.

    Args:
        session:
            Database session to use for adding and committing the new Bucket.
        bucket:
            Bucket object, containing bucket information.

    Returns:
        The newly created `Bucket` object.
    """
    session.add(bucket)
    session.commit()
    session.refresh(bucket)
    return bucket


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
    return session.get(Bucket, bucket_id)


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
    return list(session.exec(statement).all())


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
        FruitOwnerDoesNotMatchBucketOwnerError:
            If any fruit in the updated bucket does not belong to the bucket's
            owner.
    """
    bucket_data = bucket_in.model_dump(exclude_unset=True)
    db_bucket.sqlmodel_update(bucket_data)

    for fruit in db_bucket.fruits:
        if fruit.user_id != db_bucket.user_id:
            raise FruitOwnerDoesNotMatchBucketOwnerError(
                f"Fruit with ID {fruit.id} does not belong to the bucket's owner with ID {db_bucket.user_id}. Change the fruit's owner before adding it to the bucket, or change the bucket's owner to match the fruit's owner."
            )

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

    if len(bucket.fruits) > 0:
        raise BucketNotEmptyError()

    session.delete(bucket)
    session.commit()
    return bucket
