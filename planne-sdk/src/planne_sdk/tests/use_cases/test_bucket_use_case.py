from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlmodel import Session, select

from planne_sdk.db_seeder import insert
from planne_sdk.excpetions import (
    BucketCapacityExceededError,
    FruitNotFoundError,
    FruitOwnerDoesNotMatchBucketOwnerError,
)
from planne_sdk.models import Bucket, BucketCreate, Fruit, User
from planne_sdk.use_cases.bucket_use_case import (
    create_bucket,
    delete_bucket,
    get_bucket,
    get_buckets_by_user,
    update_bucket,
)


class TestCreateBucket:
    now = datetime.now(UTC)

    def test_creates_simplest_bucket(self, db_session: Session):
        user: User = insert(User, session=db_session)

        capacity = 10
        bucket = create_bucket(
            session=db_session,
            bucket=BucketCreate(user_id=user.id, capacity=capacity),
        )

        assert bucket.id is not None

        bucket = db_session.get(Bucket, bucket.id)
        assert bucket is not None
        assert bucket.user_id == user.id
        assert bucket.capacity == capacity
        assert bucket.fruits == []

    def test_creates_bucket_with_non_expired_fruits(self, db_session: Session):
        user: User = insert(User, session=db_session)
        fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )
        fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=9),
            expires_at=self.now + timedelta(minutes=4),
        )

        capacity = 3
        bucket = create_bucket(
            session=db_session,
            bucket=BucketCreate(
                user_id=user.id,
                capacity=capacity,
                fruits=[fruit_1.id, fruit_2.id],
            ),
        )

        assert bucket.id is not None

        bucket = db_session.get(Bucket, bucket.id)
        assert bucket is not None
        assert bucket.user_id == user.id
        assert bucket.capacity == capacity
        assert fruit_1 in bucket.fruits
        assert fruit_2 in bucket.fruits

    def test_raises_exc_when_creating_bucket_with_more_fruits_than_capacity(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=5),
        )
        fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=9),
            expires_at=self.now + timedelta(minutes=4),
        )

        with pytest.raises(BucketCapacityExceededError):
            capacity = 1
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=capacity,
                    fruits=[fruit_1.id, fruit_2.id],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

    def test_raises_exc_when_creating_bucket_with_inexistent_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        inexistent_fruit_id = uuid4()

        with pytest.raises(FruitNotFoundError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=3,
                    fruits=[inexistent_fruit_id],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

    def test_raises_exc_when_creating_bucket_with_expired_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )

        with pytest.raises(FruitNotFoundError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=3,
                    fruits=[expired_fruit.id],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

    def test_raises_exc_when_creating_bucket_with_fruits_from_other_user(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        user_unrelated: User = insert(User, session=db_session)

        fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now + timedelta(minutes=30),
        )
        fruit_unrelated_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            created_at=self.now - timedelta(minutes=22),
            expires_at=self.now + timedelta(minutes=12),
        )
        fruit_unrelated_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            created_at=self.now - timedelta(minutes=23),
            expires_at=self.now + timedelta(minutes=13),
        )

        with pytest.raises(FruitOwnerDoesNotMatchBucketOwnerError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=3,
                    fruits=[
                        fruit.id,
                        fruit_unrelated_1.id,
                        fruit_unrelated_2.id,
                    ],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

    def test_deletes_expired_fruits_when_creating_bucket_that_includes_them(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=8),
        )

        with pytest.raises(FruitNotFoundError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=3,
                    fruits=[expired_fruit_1.id, expired_fruit_2.id],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == 0

    def test_does_not_delete_non_expired_fruits_when_creating_bucket_that_includes_them_and_expired_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        non_expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now + timedelta(minutes=30),
        )
        expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=8),
        )

        with pytest.raises(FruitNotFoundError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=5,
                    fruits=[
                        non_expired_fruit.id,
                        expired_fruit_1.id,
                        expired_fruit_2.id,
                    ],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == 1
        assert all_fruits[0].id == non_expired_fruit.id

    def test_does_not_delete_any_unrelated_fruits_when_creating_bucket_with_expired_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        user_unrelated: User = insert(User, session=db_session)

        fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now + timedelta(minutes=30),
        )
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=21),
            expires_at=self.now - timedelta(minutes=11),
        )
        fruit_unrelated_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=22),
            expires_at=self.now + timedelta(minutes=12),
        )
        fruit_unrelated_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            created_at=self.now - timedelta(minutes=23),
            expires_at=self.now + timedelta(minutes=13),
        )
        expired_fruit_unrelated_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=24),
            expires_at=self.now - timedelta(minutes=14),
        )
        expired_fruit_unrelated_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            created_at=self.now - timedelta(minutes=25),
            expires_at=self.now - timedelta(minutes=15),
        )

        fruits_to_keep = [
            fruit_unrelated_1,
            fruit_unrelated_2,
            expired_fruit_unrelated_1,
            expired_fruit_unrelated_2,
            # `fruit` Should be kept too because it's not expired, even though
            # it's included in the bucket creation attempt with expired fruits
            fruit,
        ]

        with pytest.raises(FruitNotFoundError):
            create_bucket(
                session=db_session,
                bucket=BucketCreate(
                    user_id=user.id,
                    capacity=3,
                    fruits=[fruit.id, expired_fruit.id],
                ),
            )

        all_buckets = db_session.exec(select(Bucket)).all()
        assert len(all_buckets) == 0

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == len(fruits_to_keep)
        for f in fruits_to_keep:
            assert f in all_fruits
