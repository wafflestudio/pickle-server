from typing import Optional
from datetime import datetime

from ninja import Schema


class PostCreateSchema(Schema):
    text: str
    secret_text: str
    latitude: float
    longitude: float


class PostSchema(Schema):
    id: int
    text: str
    secret_text: str
    image: str
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: datetime
    like_count: int
    challenge_count: int
    latitude: float
    longitude: float
    is_liked: bool

    @staticmethod
    def resolve_author_name(obj):
        return obj.author.username

    @staticmethod
    def resolve_is_liked(obj):
        if not hasattr(obj, "_user_likes_post"):
            return False
        return bool(obj._user_likes_post)


class PostDetailSchema(PostSchema):
    my_challenge_id: Optional[int] = None

    @staticmethod
    def resolve_my_challenge_id(obj):
        if not hasattr(obj, "_user"):
            return

        return obj.accepted_users.filter(user=obj._user).first().id


class PostWithDistanceSchema(PostSchema):
    distance: float


class PostWithChallengeInfoSchema(PostWithDistanceSchema):
    my_challenge_id: Optional[int] = None

    @staticmethod
    def resolve_my_challenge_id(obj):
        if not hasattr(obj, "_user"):
            return

        return obj.accepted_users.filter(user=obj._user).first().id
