from django.contrib.auth import get_user_model
from django.db import models

from common.upload import convert_filename

User = get_user_model()


class ChallengeStatus(models.TextChoices):
    ACCEPTED = "accepted"
    FAILED = "failed"
    COMPLETED = "completed"


def upload_to_func(instance, filename):
    prefix = "uploads/challenge_images/"
    return prefix + convert_filename(filename)


class Challenge(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accepted_challenges"
    )
    post = models.ForeignKey(
        "post.Post", on_delete=models.CASCADE, related_name="accepted_users"
    )
    status = models.CharField(
        max_length=10, choices=ChallengeStatus.choices, default=ChallengeStatus.ACCEPTED
    )
    start_time = models.DateTimeField(auto_now_add=True)
    #
    image = models.ImageField(upload_to=upload_to_func, blank=True, null=True)
    similarity = models.IntegerField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="%(app_label)s_%(class)s_unique_user_post",
            )
        ]

    def __str__(self):
        return f"{self.user} accepted {self.post}"
