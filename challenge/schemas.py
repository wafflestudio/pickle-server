from datetime import datetime
from decimal import Decimal

from ninja import Schema


class CoordinateSchema(Schema):
    latitude: Decimal
    longitude: Decimal


class AcceptChallengeSchema(Schema):
    post_id: int


class ChallengeResponseSchema(Schema):
    id: int
    coordinate: CoordinateSchema
    start_time: datetime
