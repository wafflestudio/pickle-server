import datetime
import os

from functools import wraps


def upload_to_func(dir_name):
    @wraps(upload_to_func)
    def _upload_to_func(instance, filename):
        now = datetime.datetime.now()
        prefix = now.strftime("%Y/%m/%d")
        file_name = now.strftime("%H%M%S_") + filename.replace(" ", "_")
        extension = os.path.splitext(filename)[-1].lower()
        return "/".join(
            [
                dir_name,
                prefix,
                file_name,
                extension,
            ]
        )

    return _upload_to_func
