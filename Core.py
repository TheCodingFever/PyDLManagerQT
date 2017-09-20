from queue import Queue
import click
import os
import binascii
import threading
import requests
import time
import RegexUtility
import progressbar
import collections
import ClipboardWatcher as Watch
import sys


class Downloader(threading.Thread):
    """Threaded file downloader"""

    def __init__(self, url_queue, progress_queue, output_directory):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
        self.url_queue = url_queue
        self.progress_queue = progress_queue
        self.output_directory = output_directory
        self.progress_bar = progressbar
        self.output_lock = threading.Lock()
        self._stopping = False

    def run(self):

        while not self._stopping:

            url = self.url_queue.get()

            # download the file
            self.download_file(url)

            # send a signal to queue that job is done
            self.url_queue.task_done()
            self.stop()

    def download_file(self, url):
        t_start = time.clock()

        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:

            file_name = RegexUtility.fetch_filename(url)
            f_target_path = self.output_directory + "/" + file_name

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

            with self.output_lock:

                with open(f_target_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                            self.progress_queue.put_nowait([url, bytes_downloaded/total_length, t_start])
                r.close()
        else:
            r.close()
            print("* Thread: " + self.name + " Bad URL: " + url)

    def stop(self):
        self._stopping = True


class DownloadManager:
    """Spawns downloader threads and manages URL downloads queue"""

    def __init__(self, output_directory, download_dict, threads=5):
        self.download_dict = download_dict
        self.output_directory = output_directory
        self.url_queue = Queue()
        self.progress_queue = Queue()
        self._progress = collections.OrderedDict()
        self._workers = []
        self._thread_count = threads

    def start_watching(self):
        self.__start_workers()
        watcher = Watch.ClipboardWatcher(RegexUtility.is_downloadable_url, self.begin_download, 5.)
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
            worker = Downloader(self.url_queue, self.progress_queue, self.output_directory)
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue
    def begin_download(self, watcher_url=None):

        if watcher_url is not None:
            self.url_queue.put(watcher_url)
            self.url_queue.join()
            return

        self.__start_workers()
        for key in self.download_dict:
            self.url_queue.put(self.download_dict[key])

        self.get_progress()

        # wait for the queue to finish
        self.progress_queue.join()

        return

    def get_progress(self):
        while any(i.is_alive() for i in self._workers):
            time.sleep(0.1)
            while not self.progress_queue.empty():
                name, percent, s_time = self.progress_queue.get()
                self._progress[name] = percent, s_time
                self.print_progress()
                self.progress_queue.task_done()

    def print_progress(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        for url, (percent, s_time) in self._progress.items():
            filename = RegexUtility.fetch_filename(url)
            bar = ('=' * int(percent * 20)).ljust(20)
            percent = int(percent * 100)
            print('\r')
            sys.stdout.write(" %s:\n [%s] %s%%\n" % (filename, bar, percent))
            if percent == 100:
                t_elapsed = time.clock() - s_time
                sys.stdout.write(" Download from " + url + " completed in " + str(t_elapsed) + " seconds\n")
        sys.stdout.flush()