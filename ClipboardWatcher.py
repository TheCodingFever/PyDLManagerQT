import time
import threading
import pyperclip
import re
import os
import binascii


def is_downloadable_url(url):
    url_regex = re.compile(
        "\w+\.[A-Za-z]{3,4}(?=\?|$)")

    result = re.search(url_regex, url)
    if result is not None:
        print('Appropriate link detected!')
        return True
    else:
        return False


def print_to_stdout(clipboard_content):
    print("Found url: %s" % str(clipboard_content))


def feed_queue(clipboard_content, download_manager):

    download_manager.direct_link = clipboard_content
    download_manager.begin_download()


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, manager, pause=5):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(16)))
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
