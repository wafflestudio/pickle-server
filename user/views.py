from ninja import Router, Schema

from ninja.errors import AuthenticationError
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse

from user.models import User


router = Router(tags=["user"])


class UserCreateSchema(Schema):
    email: str
    username: str
    password: str


class UserLoginSchema(Schema):
    email: str
    password: str


class UserSchema(Schema):
    id: int
    email: str
    username: str


@router.post(
    "/signup",
    response={200: UserSchema},
    auth=None,
)
def post_signup(request, params: UserCreateSchema, response: HttpResponse):
    user = User.objects.create_user(**params.dict())
    return post_login(request, params, response)


@router.post(
    "/login",
    response={200: UserSchema},
    auth=None,
)
def post_login(request, params: UserLoginSchema, response: HttpResponse):
    user = User.objects.get(email=params.email)

    user = authenticate(request, email=params.email, password=params.password)
    if user is not None:
        login(request, user)
        response.set_cookie("sessionid", request.session.session_key)
        return response
    else:
        raise AuthenticationError("Invalid password")


@router.post("/logout")
def post_logout(request, response: HttpResponse):
    logout(request)
    response.delete_cookie("sessionid")
    return None


@router.get("/user", response={200: UserSchema})
def get_user(request):
    return request.user

