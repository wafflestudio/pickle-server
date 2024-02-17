from logging import getLogger
from math import cos, radians

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from common.db import Acos, Cos, Radians, Sin
from common.upload import convert_filename

logger = getLogger(__name__)
User = get_user_model()


def upload_to_func(instance, filename):
    prefix = "uploads/post_images/"
    return prefix + convert_filename(filename)


class Post(models.Model):
    text = models.TextField(blank=True)
    secret_text = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to_func, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    like_count = models.IntegerField(default=0)
    challenge_count = models.IntegerField(default=0)
    latitude = models.FloatField(
        _("latitude"),
        null=False,
        default=21.89975,
    )
    longitude = models.FloatField(
        _("longitude"),
        null=False,
        default=168.38367,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:100]

    @classmethod
    def filter_with_distance(
        cls,
        latitude: float,  # degree
        longitude: float,  # degree
        within: int,  # meter
    ):
        lat_in_rad = radians(latitude)
        lon_in_rad = radians(longitude)
        print("lat_in_rad: %s, lon_in_rad: %s" % (lat_in_rad, lon_in_rad))

        distance_in_meter_query = 6371000 * Acos(
            Cos(lat_in_rad)
            * Cos(Radians(F("latitude")))
            * Cos(Radians(F("longitude")) - lon_in_rad)
            + Sin(lat_in_rad) * Sin(Radians(F("latitude")))
        )

        approx_lat = within / 111000
        approx_long = within / 111000 / cos(lat_in_rad)
        print("approx_lat: %s, approx_long: %s" % (approx_lat, approx_long))

        return (
            cls.objects
            # 빠른 계산을 위해 위경도로 적당히 계산합니다.
            .filter(
                latitude__lte=latitude + approx_lat,
                latitude__gte=latitude - approx_lat,
                longitude__lte=longitude + approx_long,
                longitude__gte=longitude - approx_long,
            )
            .annotate(distance=distance_in_meter_query)
            .filter(distance__lte=within)
        )


class UserLikesPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="%(app_label)s_%(class)s_unique_user_post"
            )
        ]

    def __str__(self):
        return f"{self.user} likes {self.post}"
