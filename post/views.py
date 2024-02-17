import datetime
from typing import List

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from ninja import File, Router, Schema
from ninja.files import UploadedFile
from ninja.pagination import paginate

from common.pagination import CursorPagination
from post.models import Post
from seeya_server.exceptions import ErrorResponseSchema

router = Router(tags=["post"])


class PostCreateSchema(Schema):
    text: str


class PostSchema(Schema):
    id: int
    text: str
    image: str
    author_id: int
    author_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    like_count: int
    is_liked: bool

    @staticmethod
    def resolve_author_name(obj):
        return obj.author.username

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


@router.delete(
    "/{int:post_id}",
    response={200: None, 403: ErrorResponseSchema},
)
def post_delete(request, post_id: int):
    user = request.user
    post = Post.objects.get(id=post_id)
    if post.author != user:
        raise PermissionDenied("자신의 게시물만 삭제할 수 있습니다.")
    post.delete()


@router.get(
    "/{int:post_id}",
    response={200: PostSchema},
)
def post_get(request, post_id: int):
    user = request.user
    post = Post.objects.get(id=post_id)
    post._user_likes_post = bool(user.likes.filter(post=post).exists())
    return post


@router.get(
    "/{int:post_id}/like",
    response={200: PostSchema},
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
@paginate(CursorPagination)
def post_list(request):
    posts = Post.objects.all().prefetch_related(
        "author",
        Prefetch(
            "likes",
            queryset=request.user.likes.all(),
            to_attr="_user_likes_post",
        ),
    )
    return posts


@router.get(
    "/my/list",
    response={200: List[PostSchema]},
)
@paginate(CursorPagination)
def post_my_list(request):
    user = request.user
    posts = Post.objects.filter(author=user).prefetch_related(
        "author",
        Prefetch(
            "likes",
            queryset=request.user.likes.all(),
            to_attr="_user_likes_post",
        ),
    )
    return posts
