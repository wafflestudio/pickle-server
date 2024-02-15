import datetime
from typing import List

from ninja import File, Router, Schema
from ninja.files import UploadedFile

from user.models import User
from post.models import Post

router = Router(tags=["post"])


class PostCreateSchema(Schema):
    text: str


class PostSchema(Schema):
    text: str
    image: str
    author_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    like_count: int


@router.post(
    "/create",
    response={200: PostSchema},
)
def post_create(request, params: PostCreateSchema, image: UploadedFile = File(...)):
    user = request.user
    post = Post.objects.create(
        text=params.text,
        image=image,
        author=user,
    )
    return post


@router.get(
    "/{int:post_id}",
    response={200: PostSchema},
    auth=None,
)
def post_get(request, post_id: int):
    post = Post.objects.get(id=post_id)
    return post


@router.post(
    "/list",
    response={200: List[PostSchema]},
)
def post_list(request):
    posts = Post.objects.all()
    return posts
