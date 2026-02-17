from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlmodel import Session, select

from planne_sdk.db_seeder import insert
from planne_sdk.models import Fruit
from planne_sdk.use_cases._fruit_expiration_handler import (
    expire_fruits_if_needed,
    get_and_expire_fruits_if_needed,
    is_fruit_expired,
)


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


class TestExpireFruitsIfNeeded:
    now = datetime.now(UTC)

    def test_deletes_single_expired_fruit(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )

        expire_fruits_if_needed(db_session, expired_fruit)

        assert db_session.get(Fruit, expired_fruit.id) is None

    def test_keeps_single_non_expired_fruit(self, db_session: Session):
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        expire_fruits_if_needed(db_session, non_expired_fruit)

        result = db_session.get(Fruit, non_expired_fruit.id)
        assert result is not None
        assert result.id == non_expired_fruit.id

    def test_deletes_expired_fruits_from_list(self, db_session: Session):
        expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )
        expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=15),
        )

        expire_fruits_if_needed(db_session, [expired_fruit_1, expired_fruit_2])

        assert db_session.get(Fruit, expired_fruit_1.id) is None
        assert db_session.get(Fruit, expired_fruit_2.id) is None

    def test_keeps_non_expired_fruits_in_list(self, db_session: Session):
        non_expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )
        non_expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now + timedelta(minutes=15),
        )

        expire_fruits_if_needed(
            db_session, [non_expired_fruit_1, non_expired_fruit_2]
        )

        result_1 = db_session.get(Fruit, non_expired_fruit_1.id)
        assert result_1 is not None
        assert result_1.id == non_expired_fruit_1.id

        result_2 = db_session.get(Fruit, non_expired_fruit_2.id)
        assert result_2 is not None
        assert result_2.id == non_expired_fruit_2.id

    def test_deletes_only_expired_from_mixed_list(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        expire_fruits_if_needed(db_session, [expired_fruit, non_expired_fruit])

        expired_result = db_session.get(Fruit, expired_fruit.id)
        assert expired_result is None
        non_expired_result = db_session.get(Fruit, non_expired_fruit.id)
        assert non_expired_result is not None
        assert non_expired_result.id == non_expired_fruit.id

    def test_handles_empty_list(self, db_session: Session):
        expire_fruits_if_needed(db_session, [])

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == 0


class TestGetAndExpireFruitsIfNeeded:
    now = datetime.now(UTC)

    def test_returns_non_expired_fruits(self, db_session: Session):
        fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )
        fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now + timedelta(minutes=15),
        )

        fruits, expired_ids = get_and_expire_fruits_if_needed(
            db_session, [fruit_1.id, fruit_2.id]
        )

        assert len(fruits) == 2
        fruits_ids = [f.id for f in fruits]
        assert fruit_1.id in fruits_ids
        assert fruit_2.id in fruits_ids

        assert len(expired_ids) == 0

    def test_returns_expired_fruit_ids(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )

        fruits, expired_ids = get_and_expire_fruits_if_needed(
            db_session, [expired_fruit.id]
        )

        assert len(fruits) == 0
        assert len(expired_ids) == 1
        assert expired_fruit.id in expired_ids

    def test_returns_non_existent_fruit_ids(self, db_session: Session):
        non_existent_id = uuid4()

        fruits, expired_ids = get_and_expire_fruits_if_needed(
            db_session, [non_existent_id]
        )

        assert len(fruits) == 0
        assert len(expired_ids) == 1
        assert non_existent_id in expired_ids

    def test_deletes_expired_fruits_from_database(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )

        get_and_expire_fruits_if_needed(db_session, [expired_fruit.id])

        assert db_session.get(Fruit, expired_fruit.id) is None

    def test_keeps_non_expired_fruits_in_database(self, db_session: Session):
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        get_and_expire_fruits_if_needed(db_session, [non_expired_fruit.id])

        result = db_session.get(Fruit, non_expired_fruit.id)
        assert result is not None
        assert result.id == non_expired_fruit.id

    def test_handles_mixed_expired_and_non_expired(self, db_session: Session):
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now - timedelta(minutes=5),
        )
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        fruits, expired_ids = get_and_expire_fruits_if_needed(
            db_session, [expired_fruit.id, non_expired_fruit.id]
        )

        assert len(fruits) == 1
        assert fruits[0].id == non_expired_fruit.id
        assert db_session.get(Fruit, non_expired_fruit.id) is not None

        assert len(expired_ids) == 1
        assert expired_ids[0] == expired_fruit.id
        assert db_session.get(Fruit, expired_fruit.id) is None

    def test_handles_mixed_existent_and_non_existent(
        self, db_session: Session
    ):
        non_existent_id_1 = uuid4()
        non_existent_id_2 = uuid4()
        existent_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )

        fruits, expired_ids = get_and_expire_fruits_if_needed(
            db_session,
            [non_existent_id_1, existent_fruit.id, non_existent_id_2],
        )

        assert len(fruits) == 1
        assert fruits[0].id == existent_fruit.id
        assert db_session.get(Fruit, existent_fruit.id) is not None

        assert len(expired_ids) == 2
        assert non_existent_id_1 in expired_ids
        assert db_session.get(Fruit, non_existent_id_1) is None
        assert non_existent_id_2 in expired_ids
        assert db_session.get(Fruit, non_existent_id_2) is None
