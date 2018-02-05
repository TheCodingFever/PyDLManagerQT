import time
import threading
import pyperclip


def print_to_stdout(clipboard_content):
    print("Found url: %s" % str(clipboard_content))


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, pause=5):
        super(ClipboardWatcher, self).__init__()
        self._pause = pause
        self._predicate = predicate
        self._stopping = False
        self._callback = callback

    def run(self):
        recent_value = ""
        while not self._stopping:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    self._callback(recent_value)
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True
