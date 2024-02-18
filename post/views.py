from typing import List

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Prefetch
from ninja import File, Form, Router
from ninja.files import UploadedFile
from ninja.pagination import paginate
from challenge.schemas import ChallengeSchema, ChallengeSimpleSchema

from common.pagination import CursorPagination
from post.models import Post
from post.schemas import (
    PostCreateSchema,
    PostDetailSchema,
    PostSchema,
    PostWithDistanceSchema,
)
from seeya_server.exceptions import ErrorResponseSchema

router = Router(tags=["post"])


@router.post(
    "/",
    response={200: PostDetailSchema},
)
def post_create(
    request, params: Form[PostCreateSchema], image: UploadedFile = File(...)
):
    user = request.user
    post = Post.objects.create(
        text=params.text,
        image=image,
        author=user,
        latitude=params.latitude,
        longitude=params.longitude,
    )
    post._user = user
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
    response={200: PostDetailSchema},
)
def post_get(request, post_id: int):
    user = request.user
    post = Post.objects.get(id=post_id)
    post._user_likes_post = bool(user.likes.filter(post=post).exists())
    post._user = user
    return post


@router.post(
    "/{int:post_id}/like",
    response={200: PostDetailSchema},
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
    post._user = user
    post.save()
    return post


@router.get(
    "/{int:post_id}/challenges",
    response={200: List[ChallengeSimpleSchema]},
)
def get_post_challenges(request, post_id: int):
    post = Post.objects.get(id=post_id)
    challenges = (
        post.accepted_users.all().prefetch_related("user").order_by("-similarity")
    )
    return challenges[:3]


@router.get(
    "/",
    response={200: List[PostWithDistanceSchema]},
)
@paginate(CursorPagination)
def post_list(request, latitude: float, longitude: float):
    return (
        Post.filter_with_distance(latitude, longitude, 20000)
        .order_by("distance")
        .prefetch_related(
            "author",
            Prefetch(
                "likes",
                queryset=request.user.likes.all(),
                to_attr="_user_likes_post",
            ),
        )[:2]
    )


@router.get(
    "/liked_list",
    response={200: List[PostSchema]},
)
@paginate(CursorPagination)
def post_liked_list(request):
    posts = (
        Post.objects.filter(
            likes__user=request.user,
        )
        .order_by("-id")
        .prefetch_related(
            "author",
            Prefetch(
                "likes",
                queryset=request.user.likes.all(),
                to_attr="_user_likes_post",
            ),
        )
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
