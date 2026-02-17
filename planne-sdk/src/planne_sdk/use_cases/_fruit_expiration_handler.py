"""Private module with functions for handling fruit expiration logic.

These functions are used throughout the SDK's use cases to ensure that fruits
are properly expired whenever any user would interact with them, accomplishing
a sort of "lazy expiration" mechanism.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, col, select

from ..models import Fruit


def is_fruit_expired(fruit: Fruit) -> bool:
    """Check if a fruit is expired. Assumes `fruit.expires_at` is in UTC.

    If `fruit.expires_at` is in a timezone aware datetime, its timezone will be
    ignored and it will be treated as if it were in UTC.

    This allows the function to be flexible and work with datetimes that are
    either timezone aware or timezone naive, as long as they are in UTC or
    treated as UTC, such as what is returned by SQLModel or SQLAlchemy.
    """
    return fruit.expires_at.replace(tzinfo=None) <= datetime.now(UTC).replace(
        tzinfo=None
    )


def expire_fruits_if_needed(
    session: Session, fruit_or_fruits: Fruit | list[Fruit]
) -> None:
    """Iterate over a list of Fruit objects and delete each one as needed.

    Also accepts a single Fruit object as a shortcut for the common case of
    expiring just one fruit.

    Automatically commits the transaction if any fruits were deleted.
    """
    if fruit_or_fruits == []:
        return
    if not isinstance(fruit_or_fruits, list):
        fruit_or_fruits = [fruit_or_fruits]

    for fruit in fruit_or_fruits:
        if is_fruit_expired(fruit):
            session.delete(fruit)
    session.commit()


def get_and_expire_fruits_if_needed(
    session: Session, fruit_ids: list[UUID]
) -> tuple[list[Fruit], list[UUID]]:
    """Get a list of Fruit objects by their IDs, expiring any that are expired.

    Automatically commits the transaction if any fruits were deleted.

    Returns:
        A tuple containing two lists, the first with Fruit objects found and
        not-expired; the second with the UUIDs of Fruits that were either never
        found or that were expired and deleted in the process.
    """
    query = select(Fruit).where(col(Fruit.id).in_(fruit_ids))
    fruits = list(session.exec(query).all())

    # Initial value is all fruit_ids that were never found in the first place
    fruit_ids_expired_or_inexistent = [
        f_id
        for f_id in fruit_ids
        if f_id not in [fruit.id for fruit in fruits]
    ]
    fruits_not_expired = []

    for fruit in fruits:
        if is_fruit_expired(fruit):
            fruit_ids_expired_or_inexistent.append(fruit.id)
            session.delete(fruit)
        else:
            fruits_not_expired.append(fruit)

    session.commit()
    return fruits_not_expired, fruit_ids_expired_or_inexistent
