import os
import binascii
import threading
import requests
import time


class Downloader(threading.Thread):
    """Threaded file downloader"""

    def __init__(self, queue, output_directory):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(16)))
        self.queue = queue
        self.output_directory = output_directory

    def run(self):
        while True:
            # get url from queue
            url = self.queue.get()

            # download the file
            print("* Thread " + self.name + " - processing URL")
            self.download_file(url)

            # send a signal to queue that job is done
            self.queue.task_done()

    def download_file(self, url):
        t_start = time.clock()

        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            t_elapsed = time.clock() - t_start
            print("* Thread: " + self.name + " Downloaded " + url + " in " + str(t_elapsed) + " seconds")

            f_name = self.output_directory + "/" + os.path.basename(url)

            with open(f_name, "wb") as f:
                f.write(r.content)
        else:
            print("* Thread: " + self.name + " Bad URL: " + url)

