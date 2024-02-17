from django.db.models import Func


class Sin(Func):
    function = "SIN"


class Cos(Func):
    function = "COS"


class Acos(Func):
    function = "ACOS"


class Radians(Func):
    function = "RADIANS"
