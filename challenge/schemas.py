from datetime import datetime
from typing import Optional

from ninja import Schema

from post.schemas import PostDetailSchema


class CoordinateSchema(Schema):
    latitude: float
    longitude: float


class ChallengeAcceptSchema(Schema):
    post_id: int


class ChallengeSchema(Schema):
    id: int
    coordinate: CoordinateSchema
    start_time: datetime
    image: Optional[str]
    similarity: Optional[int]
    result: Optional[str]
    post: PostDetailSchema

    @staticmethod
    def resolve_coordinate(obj):
        return CoordinateSchema(
            latitude=obj.post.latitude, longitude=obj.post.longitude
        )
