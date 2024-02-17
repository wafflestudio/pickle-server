from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class ChallengeStatus(models.TextChoices):
    ACCEPTED = "accepted"
    FAILED = "failed"
    COMPLETED = "completed"


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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="%(app_label)s_%(class)s_unique_user_post",
            )
        ]

    def __str__(self):
        return f"{self.user} accepted {self.post}"
