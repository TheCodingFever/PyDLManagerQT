import os
import re


def compile_filename(url):
    _temp_name = os.path.basename(url)
    _regex = re.compile('\.[a-zA-Z0-9]+')
    result = re.search(_regex, _temp_name)

    return _temp_name[:result.end()]

