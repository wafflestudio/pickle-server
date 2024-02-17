import datetime
import os


def convert_filename(filename):
    now = datetime.datetime.now()
    prefix = now.strftime("%Y/%m/%d")
    file_name = now.strftime("%H%M%S_") + filename.replace(" ", "_")
    return "/".join([prefix, file_name])
