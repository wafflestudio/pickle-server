from datetime import datetime

from ninja import Schema


class CoordinateSchema(Schema):
    latitude: float
    longitude: float


class AcceptChallengeSchema(Schema):
    post_id: int


class ChallengeResponseSchema(Schema):
    id: int
    coordinate: CoordinateSchema
    start_time: datetime
