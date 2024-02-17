import re


def camel_to_snake(name):
    p = re.compile(r"(?<!^)(?=[A-Z])")
    return p.sub("_", name).lower()
