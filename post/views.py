import datetime
from typing import List

from ninja import File, Router, Schema
from ninja.files import UploadedFile

from django.db import transaction

from post.models import Post
from user.models import User

router = Router(tags=["post"])


class PostCreateSchema(Schema):
    text: str


class PostSchema(Schema):
    id: int
    text: str
    image: str
    author_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    like_count: int
    is_liked: bool

    @staticmethod
    def resolve_is_liked(obj):
        if not hasattr(obj, "_user_likes_post"):
            return False
        return bool(obj._user_likes_post)


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
    user = request.user
    post = Post.objects.get(id=post_id)
    post._user_likes_post = bool(user.likes.filter(post=post).exists())
    return post


@router.get(
    "/{int:post_id}/like",
    response={200: PostSchema},
    auth=None,
)
@transaction.atomic
def post_like(request, post_id: int):
    post = Post.objects.get(id=post_id)
    user = request.user
    if user.likes.filter(post=post).exists():
        user.likes.filter(post=post).delete()
        post.like_count -= 1
        post._user_likes_post = False
    else:
        user.likes.create(post=post)
        post.like_count += 1
        post._user_likes_post = True
    post.save()
    return post


@router.get(
    "/list",
    response={200: List[PostSchema]},
)
def post_list(request):
    from django.db.models import Prefetch

    posts = Post.objects.all().prefetch_related(
        Prefetch(
            "likes",
            queryset=request.user.likes.all(),
            to_attr="_user_likes_post",
        )
    )
    return posts
