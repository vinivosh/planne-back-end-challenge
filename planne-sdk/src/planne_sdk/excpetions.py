"""Module containing custom exceptions used in Planne SDK."""

# ruff: noqa: D101


class PlanneSDKError(Exception):
    def __init__(self, msg: str | None = None):
        """Base exception class for all exceptions raised by the Planne SDK."""
        super().__init__(msg or "Unspecified error in Planne SDK.")


class ObjectNotFoundError(PlanneSDKError):
    def __init__(self, msg: str | None = None):
        """Raised when a requested object is not found in the DB."""
        super().__init__(msg or "Requested object was not found.")


class UserNotFoundError(ObjectNotFoundError):
    def __init__(self, msg: str | None = None):
        """Raised when a requested User is not found in the DB."""
        super().__init__(msg or "Requested User was not found.")


class FruitNotFoundError(ObjectNotFoundError):
    def __init__(self, msg: str | None = None):
        """Raised when a requested Fruit is not found in the DB."""
        super().__init__(msg or "Requested Fruit was not found.")


class FruitOwnerDoesNotMatchBucketOwnerError(PlanneSDKError):
    def __init__(self, msg: str | None = None):
        """Raised when trying to add a fruit to a bucket owned by a different user."""
        super().__init__(
            msg or "Cannot add fruit to a bucket owned by a different user."
        )


class BucketNotEmptyError(PlanneSDKError):
    def __init__(self, msg: str | None = None):
        """Raised when trying to delete a bucket that still contains fruits."""
        super().__init__(
            msg or "Cannot delete a bucket that still contains fruits."
        )


class BucketCapacityExceededError(PlanneSDKError):
    def __init__(self, msg: str | None = None):
        """Raised when trying to add more fruits to a bucket than its capacity allows."""
        super().__init__(
            msg
            or "A Bucket cannot contain more fruits than its capacity allows."
        )
