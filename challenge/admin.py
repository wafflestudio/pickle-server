from django.contrib import admin

from .models import Challenge, UserAcceptChallenge

admin.site.register(Challenge)
admin.site.register(UserAcceptChallenge)
