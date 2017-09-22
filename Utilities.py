import os
import re


def fetch_filename(url):
    _temp_name = os.path.basename(url)
    _regex = re.compile('\.[a-zA-Z0-9]+')
    result = re.search(_regex, _temp_name)
    return _temp_name[:result.end()]


def is_downloadable_url(url):
    url_regex = re.compile(
        "([\/.\w]+)([[.][\w]+)(?=\?|$)")

    result = re.search(url_regex, url)
    if result is not None:
        print('Appropriate link detected!')
        return True
    else:
        print('Bad Url!')
        return False


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
