"""Fruit-related API routes (CRUD)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from planne_sdk.models import (
    Bucket,
    Fruit,
    FruitCreate,
    FruitPublic,
    FruitsPublic,
    FruitUpdate,
    Message,
)
from planne_sdk.use_cases import fruit_use_case

from api.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=FruitsPublic)
def get_fruits(
    session: SessionDep,
    current_user: CurrentUser,
) -> FruitsPublic:
    """Retrieve fruits for current user."""
    fruits = fruit_use_case.get_fruits_by_user(
        session=session, user_id=current_user.id
    )
    if fruits is None:
        fruits = []

    total_count = len(fruits)
    fruits_public = [FruitPublic.model_validate(fruit) for fruit in fruits]
    return FruitsPublic(data=fruits_public, count=total_count)


@router.post("/", response_model=FruitPublic)
def create_fruit(
    *, session: SessionDep, fruit_in: FruitCreate, current_user: CurrentUser
) -> FruitPublic:
    """Create new fruit."""
    if fruit_in.user_id is None:
        fruit_in.user_id = current_user.id
    elif fruit_in.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You can only create fruits for yourself",
        )

    fruit = fruit_use_case.create_fruit(session=session, fruit_create=fruit_in)
    return FruitPublic.model_validate(fruit)


@router.get("/bucket/{bucket_id}", response_model=FruitsPublic)
def get_fruits_by_bucket(
    bucket_id: UUID, session: SessionDep, current_user: CurrentUser
) -> FruitsPublic:
    """Get all fruits in a specific bucket."""
    bucket = session.get(Bucket, bucket_id)
    if bucket is None or (
        bucket.user_id != current_user.id and not current_user.is_superuser
    ):
        # Not returning 403 here to avoid leaking information about the
        # existence of someone else's bucket
        raise HTTPException(
            status_code=404,
            detail="The bucket with this id does not exist in the system",
        )
    del bucket

    fruits = fruit_use_case.get_fruits_by_bucket(
        session=session, bucket_id=bucket_id
    )
    if fruits is None:
        fruits = []

    fruits_public = [FruitPublic.model_validate(fruit) for fruit in fruits]
    return FruitsPublic(data=fruits_public, count=len(fruits))


@router.get("/{fruit_id}", response_model=FruitPublic)
def get_fruit_by_id(
    fruit_id: UUID, session: SessionDep, current_user: CurrentUser
) -> FruitPublic:
    """Get a specific fruit by id."""
    fruit = fruit_use_case.get_fruit(session=session, fruit_id=fruit_id)
    if fruit is None or (
        fruit.user_id != current_user.id and not current_user.is_superuser
    ):
        # Not returning 403 here to avoid leaking information about the
        # existence of someone else's fruit
        raise HTTPException(
            status_code=404,
            detail="The fruit with this id does not exist in the system",
        )
    return FruitPublic.model_validate(fruit)


@router.patch("/{fruit_id}", response_model=FruitPublic)
def update_fruit(
    *,
    session: SessionDep,
    fruit_id: UUID,
    fruit_in: FruitUpdate,
    current_user: CurrentUser,
) -> FruitPublic:
    """Update a fruit."""
    db_fruit = session.get(Fruit, fruit_id)
    if db_fruit is None or (
        db_fruit.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=404,
            detail="The fruit with this id does not exist in the system",
        )

    db_fruit = fruit_use_case.update_fruit(
        session=session, db_fruit=db_fruit, fruit_in=fruit_in
    )
    return FruitPublic.model_validate(db_fruit)


@router.delete("/{fruit_id}", response_model=Message)
def delete_fruit(
    session: SessionDep, current_user: CurrentUser, fruit_id: UUID
) -> Message:
    """Delete a fruit."""
    fruit = session.get(Fruit, fruit_id)
    if fruit is None or (
        fruit.user_id != current_user.id and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=404,
            detail="The fruit with this id does not exist in the system",
        )

    fruit_use_case.delete_fruit(session=session, fruit_id=fruit_id)
    return Message(message="Fruit deleted successfully")
