from http import HTTPStatus

from django.http import HttpRequest
from ninja import Router

from challenge.models import Challenge
from challenge.schemas import (
    AcceptChallengeSchema,
    ChallengeResponseSchema,
    CoordinateSchema,
)
from post.models import Post
from post.schemas import PostWithDistanceSchema
from seeya_server.exceptions import ErrorResponseSchema, SeeyaApiError

router = Router(tags=["challenge"])


@router.post(
    "",
    response={
        201: ChallengeResponseSchema,
        frozenset((401, 403, 404)): ErrorResponseSchema,
    },
)
def accept_challenge(request: HttpRequest, body: AcceptChallengeSchema):
    user = request.user
    post_id = body.post_id

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise SeeyaApiError("존재하지 않는 챌린지입니다.", HTTPStatus.NOT_FOUND)

    if post.author == user:
        raise SeeyaApiError(
            "자신의 게시물에는 도전할 수 없습니다.", HTTPStatus.FORBIDDEN
        )

    challenge, created = Challenge.objects.get_or_create(user=user, post=post)

    if not created:
        raise SeeyaApiError("이미 도전 중인 챌린지입니다.", HTTPStatus.FORBIDDEN)

    return HTTPStatus.CREATED, ChallengeResponseSchema(
        id=challenge.id,
        coordinate=CoordinateSchema(latitude=post.latitude, longitude=post.longitude),
        start_time=challenge.start_time,
    )


@router.get(
    "",
    response={
        200: list[PostWithDistanceSchema],
        frozenset((404, 403)): ErrorResponseSchema,
    },
    auth=None,
)
def list_challenges(request: HttpRequest, latitude: float, longitude: float):
    return Post.filter_with_distance(latitude, longitude, 5000).order_by(
        "-like_count", "distance"
    )[:8]


@router.get(
    "/today",
    response={
        200: PostWithDistanceSchema,
        frozenset((404, 403)): ErrorResponseSchema,
    },
)
def get_today_challenges(request: HttpRequest, latitude: float, longitude: float):
    posts = (
        Post.filter_with_distance(latitude, longitude, 5000)
        .filter(author__is_superuser=True)
        .select_related("author")
    )
    if not posts.exists():
        raise SeeyaApiError("근처에 오늘의 챌린지가 없습니다.", HTTPStatus.NOT_FOUND)
    return posts.first()
