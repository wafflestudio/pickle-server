from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChallengeStatus(models.TextChoices):
    ACCEPTED = "accepted"
    FAILED = "failed"
    COMPLETED = "completed"


class Challenge(models.Model):
    post = models.ForeignKey(
        "post.Post", on_delete=models.CASCADE, related_name="challenges"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)


class UserAcceptChallenge(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accepted_challenges"
    )
    challenge = models.ForeignKey(
        "Challenge", on_delete=models.CASCADE, related_name="accepted_users"
    )
    status = models.CharField(
        max_length=10, choices=ChallengeStatus.choices, default=ChallengeStatus.ACCEPTED
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ["user", "challenge"]

    def __str__(self):
        return f"{self.user} accepted {self.challenge}"
