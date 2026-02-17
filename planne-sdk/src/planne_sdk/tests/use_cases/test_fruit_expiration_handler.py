from datetime import UTC, datetime, timedelta

# import pytest
from sqlmodel import Session, SQLModel, select

from planne_sdk.db_seeder import insert
from planne_sdk.models import Fruit
from planne_sdk.use_cases._fruit_expiration_handler import is_fruit_expired


class TestIsFruitExpired:
    now = datetime.now(UTC)

    def test_returns_true_for_expired_fruit(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )

        assert is_fruit_expired(expired_fruit)

    def test_returns_false_for_non_expired_fruit(self, db_session: Session):
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        assert not is_fruit_expired(non_expired_fruit)
