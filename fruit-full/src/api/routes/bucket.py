"""Bucket-related API routes (CRUD)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from planne_sdk.excpetions import (
    BucketCapacityExceededError,
    BucketNotEmptyError,
    BucketNotFoundError,
    FruitNotFoundError,
    FruitOwnerDoesNotMatchBucketOwnerError,
    ObjectNotFoundError,
    PlanneSDKError,
)
from planne_sdk.models import (
    Bucket,
    BucketCreate,
    BucketPublic,
    BucketsPublic,
    BucketUpdate,
    Message,
)
from planne_sdk.use_cases import bucket_use_case

from api.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=BucketsPublic)
def get_buckets(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> BucketsPublic:
    """Retrieve buckets for current user."""
    buckets = bucket_use_case.get_buckets_by_user(
        session=session, user_id=current_user.id
    )

    total_count = len(buckets)
    buckets = buckets[skip : skip + limit]

    buckets_public = [
        BucketPublic.model_validate(bucket) for bucket in buckets
    ]
    return BucketsPublic(data=buckets_public, count=total_count)


@router.post("/", response_model=BucketPublic)
def create_bucket(
    *, session: SessionDep, bucket_in: BucketCreate, current_user: CurrentUser
) -> BucketPublic:
    """Create new bucket."""
    if bucket_in.user_id is None:
        bucket_in.user_id = current_user.id
    elif (
        bucket_in.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only create buckets for yourself",
        )

    try:
        bucket = bucket_use_case.create_bucket(
            session=session, bucket=bucket_in
        )
    except (FruitNotFoundError, FruitOwnerDoesNotMatchBucketOwnerError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    return BucketPublic.model_validate(bucket)


@router.get("/{bucket_id}", response_model=BucketPublic)
def get_bucket_by_id(
    bucket_id: UUID, session: SessionDep, current_user: CurrentUser
) -> BucketPublic:
    """Get a specific bucket by id."""
    bucket = bucket_use_case.get_bucket(session=session, bucket_id=bucket_id)
    if bucket is None or (
        bucket.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=404,
            detail="The bucket with this id does not exist in the system",
        )
    return BucketPublic.model_validate(bucket)


@router.patch("/{bucket_id}", response_model=BucketPublic)
def update_bucket(
    *,
    session: SessionDep,
    bucket_id: UUID,
    bucket_in: BucketUpdate,
    current_user: CurrentUser,
) -> BucketPublic:
    """Update a bucket."""
    db_bucket = session.get(Bucket, bucket_id)
    if db_bucket is None or (
        db_bucket.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=404,
            detail="The bucket with this id does not exist in the system",
        )

    if (
        bucket_in.user_id is not None
        and bucket_in.user_id != current_user.id
        and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only assign buckets to yourself",
        )

    try:
        db_bucket = bucket_use_case.update_bucket(
            session=session, db_bucket=db_bucket, bucket_in=bucket_in
        )
    except (FruitNotFoundError, FruitOwnerDoesNotMatchBucketOwnerError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    return BucketPublic.model_validate(db_bucket)


@router.delete("/{bucket_id}", response_model=Message)
def delete_bucket(
    session: SessionDep, current_user: CurrentUser, bucket_id: UUID
) -> Message:
    """Delete a bucket."""
    bucket = session.get(Bucket, bucket_id)
    if bucket is None or (
        bucket.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=404,
            detail="The bucket with this id does not exist in the system",
        )

    try:
        bucket_use_case.delete_bucket(session=session, bucket_id=bucket_id)
    except BucketNotEmptyError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    return Message(message="Bucket deleted successfully")
