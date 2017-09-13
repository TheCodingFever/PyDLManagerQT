import time
import threading
import pyperclip
import re


def is_downloadable_url(url):
    url_regex = re.compile(
        "(?:([^:\/?#]+):)?(?:\/\/([^\/?#]*))?([^?#]*\.(?:[a-zA-Z0-9]{3}))(?:\?([^#]*))?(?:#(.*))?")
    if re.match(url_regex, url) is not None:
        return True
    else:
        return False


def print_to_stdout(clipboard_content):
    print("Found url: %s" % str(clipboard_content))


def feed_queue(clipboard_content, download_manager):

    download_manager.DownloadManager.begin_download(direct_link=clipboard_content)


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, manager, pause=5):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._pause = pause
        self._stopping = False
        self._manager = manager

    def run(self):
        recent_value = ""
        while not self._stopping:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    feed_queue(recent_value, self._manager)
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True
