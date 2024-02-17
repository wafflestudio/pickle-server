from django.contrib.auth import authenticate, login, logout
from ninja import File, Form, Router
from ninja.errors import AuthenticationError
from ninja.files import UploadedFile
from openai.resources.beta.threads import runs

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
def post_signup(request, params: Form[UserCreateIn], image: UploadedFile = File(None)):
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


@router.post(
    "/timetable",
)
def post_timetable(request, image: UploadedFile = File(...)):
    from user.utils import run
    from PIL import Image

    input_bytes = image.read()
    output_image: Image = run(input_bytes)

    # save image to file
    output_image.save("output.png")

    image_bytes = output_image.tobytes()

    from django.http import HttpResponse

    return HttpResponse(image_bytes, content_type="image/png")
