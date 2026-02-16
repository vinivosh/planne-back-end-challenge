"""Module containing custom exceptions used in Planne SDK."""

# ruff: noqa: D101


class PlanneSDKError(Exception):
    def __init__(self, msg: str | None = None):
        """Base exception class for all exceptions raised by the Planne SDK."""
        super().__init__(msg or "Unspecified error in Planne SDK.")


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
