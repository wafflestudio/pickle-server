from typing import Optional

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from ninja import File, Router
from ninja.files import UploadedFile
from ninja.errors import AuthenticationError

from user.models import User
from user.schemas import UserCreateIn, UserLoginIn, UserSchema

router = Router(tags=["user"])


@router.get(
    "/check_email",
    response={frozenset({200, 400}): None},
    auth=None,
)
def get_check_email(request, email: str):
    is_exists = User.objects.filter(email=email).exists()

    if is_exists:
        return (400, None)


@router.get(
    "/check_username",
    response={frozenset({200, 400}): None},
    auth=None,
)
def get_check_username(request, username: str):
    is_exists = User.objects.filter(username=username).exists()

    if is_exists:
        return (400, None)


@router.post(
    "/signup",
    response={200: UserSchema},
    auth=None,
)
def post_signup(request, params: UserCreateIn, image: UploadedFile = File(None)):
    user = User.objects.create_user(**params.dict(), image=image)
    return post_login(request, params)


@router.post(
    "/login",
    response={200: UserSchema},
    auth=None,
)
def post_login(request, params: UserLoginIn):
    user = User.objects.get(email=params.email)

    user = authenticate(request, email=params.email, password=params.password)
    if user is not None:
        login(request, user)
        return user
    else:
        raise AuthenticationError("Invalid password")


@router.post("/logout")
def post_logout(request):
    logout(request)
    return None


@router.get("/me", response={200: UserSchema})
def get_user_me(request):
    return request.user
