from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.security import django_auth

from challenge.models import Challenge
from post.models import Post
from seeya_server.exceptions import ErrorResponseSchema, SeeyaApiError

router = Router(tags=["challenge"])


class CoordinateSchema(Schema):
    latitude: Decimal
    longitude: Decimal


class AcceptChallengeSchema(Schema):
    post_id: int


class ChallengeResponseSchema(Schema):
    id: int
    coordinate: CoordinateSchema
    start_time: datetime


@router.post(
    "",
    response={
        201: ChallengeResponseSchema,
        frozenset((403, 404)): ErrorResponseSchema,
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
