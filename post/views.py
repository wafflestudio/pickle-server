from decimal import Decimal
from math import radians
from typing import List

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, FloatField, Prefetch
from ninja import File, Form, Router
from ninja.files import UploadedFile
from ninja.pagination import paginate

from common.db import Acos, Cos, Radians, Sin
from common.pagination import CursorPagination
from post.models import Post
from post.schemas import PostCreateSchema, PostSchema, PostWithDistanceSchema
from seeya_server.exceptions import ErrorResponseSchema

router = Router(tags=["post"])


@router.post(
    "/",
    response={200: PostSchema},
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
    "/",
    response={200: List[PostWithDistanceSchema]},
)
@paginate(CursorPagination)
def post_list(request, latitude: Decimal, longitude: Decimal):
    distance_in_meter_query = 6371000 * Acos(
        Cos(radians(latitude))
        * Cos(Radians(F("latitude"), output_field=FloatField()))
        * Cos(Radians(F("longitude"), output_field=FloatField()) - radians(longitude))
        + Sin(radians(latitude))
        * Sin(Radians(F("latitude"), output_field=FloatField()))
    )

    posts = (
        Post.objects.all()
        # 빠른 계산을 위해 위경도 0.01도 이내의 게시물만 가져옵니다.
        # 서울 기준 위도 0.01도가 약 1.1km, 경도 0.01도가 약 0.88km 입니다.
        .filter(
            latitude__lte=latitude + Decimal(0.01),
            latitude__gte=latitude - Decimal(0.01),
            longitude__lte=longitude + Decimal(0.01),
            longitude__gte=longitude - Decimal(0.01),
        )
        .annotate(distance=distance_in_meter_query)
        .filter(distance__lte=1000)
        .order_by("distance")
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
