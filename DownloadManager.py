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
import sys


class Downloader(threading.Thread):
    """Threaded file downloader"""

    def __init__(self, queue, output_directory, url):
        threading.Thread.__init__(self, name=binascii.hexlify(os.urandom(8)))
        self.queue = queue
        self.output_directory = output_directory
        self.progress_bar = progressbar
        self.output_lock = threading.Lock()
        self._url = url

    def run(self):
            # download the file
            self.download_file(self._url)

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

            with open(f_name, "wb") as f:
                for chunk in r.iter_content(chunk_size):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        self.queue.put([self.name, bytes_downloaded, total_length])
            t_elapsed = time.clock() - t_start
            print("* Thread: " + self.name + " Downloaded " + url + " in " + str(t_elapsed) + " seconds\n")
            r.close()

        else:
            r.close()
            print("* Thread: " + self.name + " Bad URL: " + url)


class DownloadManager:
    """Spawns downloader threads and manages URL downloads queue"""

    def __init__(self, output_directory, download_dict):
        self.download_dict = download_dict
        self.output_directory = output_directory
        self.queue = Queue()
        self._progress = collections.OrderedDict()
        self._workers = []

    def start_watching(self):
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
        for key in self.download_dict:
            worker = Downloader(self.queue, self.output_directory, self.download_dict[key])
            worker.setDaemon(True)
            worker.start()
            self._progress[worker.name] = 0, 0
            self._workers.append(worker)

    # Start the downloader threads, fill the queue with the URLs and
    # then feed the threads URLs via the queue
    def begin_download(self, add_url=None):

        if add_url is not None:
            dict(self.download_dict).clear()
            self.download_dict[os.urandom(5)] = add_url

        self.__start_workers()

        while any(i.is_alive() for i in self._workers):
            time.sleep(0.1)
            while not self.queue.empty():
                name, bytes_downloaded, total_bytes = self.queue.get()
                self._progress[name] = bytes_downloaded, total_bytes
                self.print_progress()

        # wait for the queue to finish
        #self.queue.join()

        return

    def print_progress(self):

        sys.stdout.write('\033[2J\033[H')  # clear screen

        bar_widgets = [
            ' [', progressbar.Timer(), '] ',
            progressbar.Bar(marker="∎", left="[", right=" "), progressbar.Percentage(), " ",
            progressbar.FileTransferSpeed(), "] ",
            ' (', progressbar.ETA(), ') ',
        ]

        for name, downloaded, total in self._progress.items():
            print("* Thread " + name + " - processing URL")
            bar = progressbar.ProgressBar(max_value=total, widgets=bar_widgets)
            if downloaded <= 1024:
                bar.start()
            bar.update(downloaded)
            if downloaded == total:
                bar.finish()
        progressbar.streams.flush()





