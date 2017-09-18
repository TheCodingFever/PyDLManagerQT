from queue import Queue
import click
import os
import binascii
import threading
import requests
import time
import HelpUtility
import progressbar
import collections
import ClipboardWatcher as Watch


class Downloader(threading.Thread):
    """Threaded file downloader"""

    def __init__(self, queue, output_directory):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
        self.queue = queue
        self.output_directory = output_directory
        self.progress_bar = progressbar
        self.output_lock = threading.Lock()

    def run(self):
        while True:

            url = self.queue.get()

            # download the file
            self.download_file(url)

            # send a signal to queue that job is done
            self.queue.task_done()

    def download_file(self, url):
        t_start = time.clock()

        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:

            f_name = self.output_directory + "/" + HelpUtility.compile_filename(url)

            try:
                total_length = int(r.headers.get('content-length'))
            except TypeError:
                print('ERROR: Bad Url or content is unreachable')
                return

            bytes_downloaded = 0

            if total_length / 1024 < 1024:
                chunk_size = 128
            else:
                chunk_size = 1024

            bar_widgets = [
                  ' [', progressbar.Timer(), '] ',
                  progressbar.Bar(marker="∎", left="[", right=" "), progressbar.Percentage(), " ",
                  progressbar.FileTransferSpeed(), "] ",
                  ' (', progressbar.ETA(), ') ',
              ]

            print("* Thread " + self.name + " - processing URL")

            with self.output_lock:
                bar = progressbar.ProgressBar(max_value=total_length, widgets=bar_widgets)
                with open(f_name, "wb") as f:
                    for chunk in r.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                            bar.update(bytes_downloaded)
                    bar.finish('\r')
                t_elapsed = time.clock() - t_start
                print("* Thread: " + self.name + " Downloaded " + url + " in " + str(t_elapsed) + " seconds\n")
                r.close()
        else:
            r.close()
            print("* Thread: " + self.name + " Bad URL: " + url)


class DownloadManager:
    """Spawns downloader threads and manages URL downloads queue"""

    def __init__(self, output_directory, download_dict, threads=5):
        self.download_dict = download_dict
        self.output_directory = output_directory
        self.queue = Queue()
        self._progress = collections.OrderedDict()
        self._workers = []
        self._thread_count = threads

    def start_watching(self):
        self.__start_workers()
        watcher = Watch.ClipboardWatcher(HelpUtility.is_downloadable_url, self.begin_download, 5.)
        watcher.setDaemon(True)
        watcher.start()

        click.echo("""
        ----------------PyDownload---------------
                Watching your clipboard...     
                Press Any Key to exit         
        -----------------------------------------""")

        choice = ''
        while choice is '':
            try:
                # time.sleep(10)
                choice = input()
            except KeyboardInterrupt:
                break
        watcher.stop()

    def __start_workers(self):

        # Creating a thread pool and pass them a queue
        for i in range(self._thread_count):
            worker = Downloader(self.queue, self.output_directory)
            worker.setDaemon(True)
            worker.start()
            self._progress[worker.name] = 0, 0
            self._workers.append(worker)

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue
    def begin_download(self, watcher_url=None):

        if watcher_url is not None:
            self.queue.put(watcher_url)
            self.queue.join()
            return

        self.__start_workers()
        for key in self.download_dict:
            self.queue.put(self.download_dict[key])

        # wait for the queue to finish
        self.queue.join()

        return









