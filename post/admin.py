from django.contrib import admin

from .models import Post, UserLikesPost

admin.site.register(Post)
admin.site.register(UserLikesPost)
