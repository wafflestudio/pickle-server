from datetime import datetime
from decimal import Decimal
from typing import Optional

from ninja import Schema


class CoordinateSchema(Schema):
    latitude: Decimal
    longitude: Decimal


class ChallengeAcceptSchema(Schema):
    post_id: int


class ChallengeSchema(Schema):
    id: int
    coordinate: CoordinateSchema
    start_time: datetime
    image: str
    similarity: Optional[int]
    result: Optional[str]

    @staticmethod
    def resolve_coordinate(obj):
        return CoordinateSchema(
            latitude=obj.post.latitude, longitude=obj.post.longitude
        )
