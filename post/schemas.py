from datetime import datetime
from decimal import Decimal

from ninja import Schema


class PostCreateSchema(Schema):
    text: str
    latitude: Decimal
    longitude: Decimal


class PostSchema(Schema):
    id: int
    text: str
    image: str
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: datetime
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
