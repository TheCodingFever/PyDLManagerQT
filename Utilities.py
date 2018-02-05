import os
import re


def fetch_filename(url):
    _temp_name = os.path.basename(url)
    _regex = re.compile('\.[a-zA-Z0-9]+')
    result = re.search(_regex, _temp_name)
    return _temp_name[:result.end()]


def is_url(url):
    url_regex = re.compile(
        "^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$")
    result = re.search(url_regex, url)
    if result is not None:
        return True
    else:
        print('Bad Url!')
        return False


def is_downloadable_url(headers):
    if str.__contains__(headers, 'image') \
            or str.__contains__(headers, 'audio') \
            or str.__contains__(headers, 'video'):
        print('Appropriate link detected!')
        return True
    else:
        print('Bad Url! Nothing to download')
        return False


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
