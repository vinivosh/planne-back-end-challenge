from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlmodel import Session, select

from planne_sdk.db_seeder import insert
from planne_sdk.excpetions import (
    BucketCapacityExceededError,
    BucketNotEmptyError,
    FruitNotFoundError,
    FruitOwnerDoesNotMatchBucketOwnerError,
)
from planne_sdk.models import Bucket, BucketCreate, BucketUpdate, Fruit, User
from planne_sdk.use_cases.bucket_use_case import (
    create_bucket,
    delete_bucket,
    get_bucket,
    get_buckets_by_user,
    update_bucket,
)


class TestGetBucket:
    now = datetime.now(UTC)

    def test_returns_existing_bucket(self, db_session: Session):
        user: User = insert(User, session=db_session)
        capacity = 5
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=capacity
        )

        result = get_bucket(session=db_session, bucket_id=bucket.id)

        assert result is not None
        assert result.id == bucket.id
        assert result.user_id == user.id
        assert result.capacity == capacity

    def test_returns_none_for_non_existent_bucket(self, db_session: Session):
        non_existent_id = uuid4()

        result = get_bucket(session=db_session, bucket_id=non_existent_id)

        assert result is None

    def test_returns_bucket_with_non_expired_fruits(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=10),
        )
        fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=5),
            expires_at=self.now + timedelta(minutes=15),
        )

        result = get_bucket(session=db_session, bucket_id=bucket.id)

        assert result is not None
        assert len(result.fruits) == 2
        assert fruit_1 in result.fruits
        assert fruit_2 in result.fruits

    def test_deletes_only_related_and_expired_fruits_when_getting_bucket(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        bucket_unrelated: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=10
        )
        fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=18),
            expires_at=self.now + timedelta(minutes=8),
        )
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        fruit_unrelated: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_unrelated,
            created_at=self.now - timedelta(minutes=18),
            expires_at=self.now + timedelta(minutes=8),
        )
        expired_fruit_unrelated: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_unrelated,
            created_at=self.now - timedelta(minutes=19),
            expires_at=self.now - timedelta(minutes=9),
        )

        result = get_bucket(session=db_session, bucket_id=bucket.id)

        assert result is not None
        assert len(result.fruits) == 1
        assert expired_fruit not in result.fruits
        assert result.fruits[0].id == fruit.id

        fruits_to_keep = [fruit, fruit_unrelated, expired_fruit_unrelated]

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == len(fruits_to_keep)
        for f in fruits_to_keep:
            assert f in all_fruits


class TestGetBucketsByUser:
    now = datetime.now(UTC)

    def test_returns_all_buckets_for_user(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket_1: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        bucket_2: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=10
        )
        bucket_3: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=15
        )

        result = get_buckets_by_user(session=db_session, user_id=user.id)

        assert len(result) == 3
        assert bucket_1 in result
        assert bucket_2 in result
        assert bucket_3 in result

    def test_returns_empty_list_for_user_with_no_buckets(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)

        result = get_buckets_by_user(session=db_session, user_id=user.id)

        assert len(result) == 0

    def test_returns_only_buckets_for_specified_user(
        self, db_session: Session
    ):
        user_1: User = insert(User, session=db_session)
        user_2: User = insert(User, session=db_session)
        bucket_user_1: Bucket = insert(
            Bucket, session=db_session, user=user_1, capacity=5
        )
        bucket_user_2: Bucket = insert(
            Bucket, session=db_session, user=user_2, capacity=10
        )

        result = get_buckets_by_user(session=db_session, user_id=user_1.id)

        assert len(result) == 1
        assert bucket_user_1 in result
        assert bucket_user_2 not in result

    def test_deletes_only_expired_fruits_in_buckets_belonging_to_user(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket_1: Bucket = insert(Bucket, session=db_session, user=user)
        bucket_2: Bucket = insert(Bucket, session=db_session, user=user)

        fruit_bucket_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_1,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=10),
        )
        expired_fruit_bucket_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_1,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        fruit_bucket_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_2,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now + timedelta(minutes=5),
        )
        expired_fruit_bucket_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket_2,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=5),
        )

        user_unrelated: User = insert(User, session=db_session)
        bucket_unrelated: Bucket = insert(
            Bucket, session=db_session, user=user_unrelated
        )
        fruit_unrelated: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            bucket=bucket_unrelated,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now + timedelta(minutes=5),
        )
        expired_fruit_unrelated: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_unrelated,
            bucket=bucket_unrelated,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=5),
        )

        result = get_buckets_by_user(session=db_session, user_id=user.id)

        assert len(result) == 2
        bucket_1_result = [b for b in result if b.id == bucket_1.id][0]
        bucket_2_result = [b for b in result if b.id == bucket_2.id][0]

        assert len(bucket_1_result.fruits) == 1
        assert fruit_bucket_1 in bucket_1_result.fruits
        assert expired_fruit_bucket_1 not in bucket_1_result.fruits

        assert len(bucket_2_result.fruits) == 1
        assert fruit_bucket_2 in bucket_2_result.fruits
        assert expired_fruit_bucket_2 not in bucket_2_result.fruits

        fruits_to_keep = [
            fruit_bucket_1,
            fruit_bucket_2,
            fruit_unrelated,
            expired_fruit_unrelated,
        ]

        all_fruits = db_session.exec(select(Fruit)).all()
        assert len(all_fruits) == len(fruits_to_keep)
        for f in fruits_to_keep:
            assert f in all_fruits


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


class TestUpdateBucket:
    now = datetime.now(UTC)

    def test_updates_bucket_capacity(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )

        new_capacity = 10
        updated_bucket = update_bucket(
            session=db_session,
            db_bucket=bucket,
            bucket_in=BucketUpdate(capacity=new_capacity),
        )

        assert updated_bucket.capacity == new_capacity

    def test_updates_empty_bucket_user_id(self, db_session: Session):
        user_1: User = insert(User, session=db_session)
        user_2: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user_1, capacity=5
        )

        updated_bucket = update_bucket(
            session=db_session,
            db_bucket=bucket,
            bucket_in=BucketUpdate(user_id=user_2.id),
        )

        assert updated_bucket.user_id == user_2.id

    def test_updates_bucket_fruits(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
        )
        fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
        )

        updated_bucket = update_bucket(
            session=db_session,
            db_bucket=bucket,
            bucket_in=BucketUpdate(fruits=[fruit_1.id, fruit_2.id]),
        )

        assert len(updated_bucket.fruits) == 2
        assert fruit_1 in updated_bucket.fruits
        assert fruit_2 in updated_bucket.fruits

    def test_raises_exc_when_updating_with_expired_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )

        with pytest.raises(FruitNotFoundError):
            update_bucket(
                session=db_session,
                db_bucket=bucket,
                bucket_in=BucketUpdate(fruits=[expired_fruit.id]),
            )

    def test_raises_exc_when_updating_with_non_existent_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        non_existent_id = uuid4()

        with pytest.raises(FruitNotFoundError):
            update_bucket(
                session=db_session,
                db_bucket=bucket,
                bucket_in=BucketUpdate(fruits=[non_existent_id]),
            )

    def test_raises_exc_when_updating_with_fruits_from_wrong_user(
        self, db_session: Session
    ):
        user_1: User = insert(User, session=db_session)
        user_2: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user_1, capacity=5
        )
        fruit_wrong_user: Fruit = insert(
            Fruit,
            session=db_session,
            user=user_2,
        )

        with pytest.raises(FruitOwnerDoesNotMatchBucketOwnerError):
            update_bucket(
                session=db_session,
                db_bucket=bucket,
                bucket_in=BucketUpdate(fruits=[fruit_wrong_user.id]),
            )

    def test_raises_exc_when_updating_with_more_fruits_than_capacity(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=1
        )
        fruit_1: Fruit = insert(Fruit, session=db_session, user=user)
        fruit_2: Fruit = insert(Fruit, session=db_session, user=user)

        with pytest.raises(BucketCapacityExceededError):
            update_bucket(
                session=db_session,
                db_bucket=bucket,
                bucket_in=BucketUpdate(fruits=[fruit_1.id, fruit_2.id]),
            )

    def test_deletes_expired_fruits_when_updating_bucket_with_them(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        expired_fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )

        with pytest.raises(FruitNotFoundError):
            update_bucket(
                session=db_session,
                db_bucket=bucket,
                bucket_in=BucketUpdate(fruits=[expired_fruit.id]),
            )

        result_fruit = db_session.get(Fruit, expired_fruit.id)
        assert result_fruit is None

    def test_updates_multiple_fields_at_once(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )

        new_capacity = 15
        new_user: User = insert(User, session=db_session)
        new_fruit: Fruit = insert(Fruit, session=db_session, user=new_user)

        updated_bucket = update_bucket(
            session=db_session,
            db_bucket=bucket,
            bucket_in=BucketUpdate(
                capacity=new_capacity,
                user_id=new_user.id,
                fruits=[new_fruit.id],
            ),
        )

        assert updated_bucket.capacity == new_capacity
        assert updated_bucket.user_id == new_user.id
        assert len(updated_bucket.fruits) == 1
        assert new_fruit in updated_bucket.fruits


class TestDeleteBucket:
    now = datetime.now(UTC)

    def test_deletes_empty_bucket(self, db_session: Session):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )

        deleted_bucket = delete_bucket(session=db_session, bucket_id=bucket.id)

        assert deleted_bucket is not None
        assert deleted_bucket.id == bucket.id

        result = db_session.get(Bucket, bucket.id)
        assert result is None

    def test_returns_none_when_deleting_non_existent_bucket(
        self, db_session: Session
    ):
        non_existent_id = uuid4()

        deleted_bucket = delete_bucket(
            session=db_session, bucket_id=non_existent_id
        )

        assert deleted_bucket is None

    def test_raises_exc_when_deleting_bucket_with_non_expired_fruits(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=10),
            expires_at=self.now + timedelta(minutes=10),
        )

        with pytest.raises(BucketNotEmptyError):
            delete_bucket(session=db_session, bucket_id=bucket.id)

        result_bucket = db_session.get(Bucket, bucket.id)
        result_fruit = db_session.get(Fruit, fruit.id)
        assert result_bucket is not None
        assert result_fruit is not None

    def test_deletes_bucket_and_fruits_if_all_its_fruits_are_expired(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=5),
        )

        deleted_bucket = delete_bucket(session=db_session, bucket_id=bucket.id)

        assert deleted_bucket is not None
        assert deleted_bucket.id == bucket.id

        result_bucket = db_session.get(Bucket, bucket.id)
        result_fruit_1 = db_session.get(Fruit, expired_fruit_1.id)
        result_fruit_2 = db_session.get(Fruit, expired_fruit_2.id)
        assert result_bucket is None
        assert result_fruit_1 is None
        assert result_fruit_2 is None

    def test_deletes_expired_fruits_even_if_deletion_fails(
        self, db_session: Session
    ):
        user: User = insert(User, session=db_session)
        bucket: Bucket = insert(
            Bucket, session=db_session, user=user, capacity=5
        )
        fruit: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now + timedelta(minutes=15),
        )
        expired_fruit_1: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=20),
            expires_at=self.now - timedelta(minutes=10),
        )
        expired_fruit_2: Fruit = insert(
            Fruit,
            session=db_session,
            user=user,
            bucket=bucket,
            created_at=self.now - timedelta(minutes=15),
            expires_at=self.now - timedelta(minutes=5),
        )

        with pytest.raises(BucketNotEmptyError):
            delete_bucket(session=db_session, bucket_id=bucket.id)

        result_bucket = db_session.get(Bucket, bucket.id)
        assert result_bucket is not None
        result_fruit = db_session.get(Fruit, fruit.id)
        assert result_fruit is not None
