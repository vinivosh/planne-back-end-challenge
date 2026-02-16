"""Module containing login-related routes."""

from datetime import timedelta
from typing import Annotated, Any

import planne_sdk.auth as auth
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from planne_sdk.models import Token, UserPublic
from planne_sdk.use_cases import user_use_case

import constants as c
from api.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/access-token")
def login_access_token(
    response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Get an OAuth2 compatible token login.

    The token is used for providing an access token for future requests.

    Args:
        response:
            The HTTP response object to set the token cookie on.
        session:
            Database session to use for authenticating the user.
        form_data:
            The OAuth2 password request form containing the username (email)
            and password.

    Returns:
        A `Token` object containing the newly generated access token.

    Raises:
        HTTPException:
            If the email or password is incorrect (status code 400).
    """
    user = user_use_case.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=c.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = auth.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    auth.set_token_cookie(response, access_token)

    return Token(access_token=access_token)


@router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """Verify the validity of an access token.

    Args:
        current_user:
            The currently authenticated user, automatically obtained from the
            access token.

    Returns:
        The `UserPublic` representation of the current user.
    """
    return current_user
