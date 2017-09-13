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

        if not os.path.exists(self.output_directory):
            print('Specified path "%s" does not exist. Creating...' % os.path.dirname(self.output_directory))
            os.makedirs(self.output_directory)

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

    def __init__(self, download_dict, output_directory, thread_count=5):
        self.thread_count = thread_count
        self.download_dict = download_dict
        self.output_directory = output_directory

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue
    def begin_download(self):
        queue = Queue()

        # Creating a thread pool and pass them a queue
        for i in range(self.thread_count):
            t = Downloader(queue, self.output_directory)
            t.setDaemon(True)
            t.start()

        # Load the queue from download dict

        for linkname in self.download_dict:
            # print uri
            queue.put(self.download_dict[linkname])

        # wait for the queue to finish
        queue.join()

        return
