from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.upload import convert_filename

User = get_user_model()


def upload_to_func(instance, filename):
    prefix = "uploads/post_images/"
    return prefix + convert_filename(filename)


class Post(models.Model):
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_to_func, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    like_count = models.IntegerField(default=0)
    challenge_count = models.IntegerField(default=0)
    latitude = models.DecimalField(
        _("latitude"),
        null=False,
        max_digits=9,
        decimal_places=6,
        default="21.89975",
    )
    longitude = models.DecimalField(
        _("longitude"),
        null=False,
        max_digits=9,
        decimal_places=6,
        default="168.38367",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:100]


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
