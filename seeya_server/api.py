from django.conf import settings
from ninja import NinjaAPI
from ninja.security import django_auth

api = NinjaAPI(auth=django_auth)

from user.views import router as user_router
from post.views import router as post_router

api.add_router("user/", user_router)
api.add_router("post/", post_router)

"""
"""

from seeya_server.exceptions import api_exception_response

if not settings.DEBUG:

    @api.exception_handler(Exception)
    def api_exception_handler(request, exc):
        response, status_code = api_exception_response(request, exc)
        return api.create_response(request, response, status=status_code)
