from queue import Queue
import os
import binascii
import threading
import requests
import time
import HelpUtility
import progressbar


class Downloader(threading.Thread):
    """Threaded file downloader"""

    def __init__(self, queue, output_directory):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(16)))
        self.queue = queue
        self.output_directory = output_directory
        self.progress_bar = progressbar

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
        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:

            bar_widgets = [
                ' [', progressbar.Timer(), '] ',
                progressbar.Bar(marker="∎", left="[", right=" "), progressbar.Percentage(), " ",
                progressbar.FileTransferSpeed(), "] ",
                ' (', progressbar.ETA(), ') ',
            ]

            f_name = self.output_directory + "/" + HelpUtility.compile_filename(url)
            total_length = int(r.headers.get('content-length'))
            bytes_downloaded = 0
            chunk_size = 1024

            with progressbar.ProgressBar(max_value=total_length, widgets=bar_widgets) as bar:
                bar.start()
                with open(f_name, "wb") as f:
                    for chunk in r.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                            bar.update(bytes_downloaded)
                    t_elapsed = time.clock() - t_start
            r.close()
            print("* Thread: " + self.name + " Downloaded " + url + " in " + str(int(t_elapsed)) + " seconds")
        else:
            r.close()
            print("* Thread: " + self.name + " Bad URL: " + url)


class DownloadManager:
    """Spawns downloader threads and manages URL downloads queue"""

    def __init__(self, output_directory, download_dict, thread_count=5):
        self.thread_count = thread_count
        self.download_dict = download_dict
        self.output_directory = output_directory
        self.queue = Queue()

        # Creating a thread pool and pass them a queue
        for i in range(self.thread_count):
            t = Downloader(self.queue, self.output_directory)
            t.setDaemon(True)
            t.start()

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue
    def begin_download(self, direct_link=None):
        # queue = Queue()

        if direct_link is not None:
            self.queue.put(direct_link)
            self.queue.join()
            return
        # Load the queue from download dict
        for linkname in self.download_dict:
            # print uri
            self.queue.put(self.download_dict[linkname])

        # wait for the queue to finish
        self.queue.join()

        return
