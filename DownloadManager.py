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

            f_name = self.output_directory + "/" + RegexUtility.compile_filename(url)

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

            print("* Thread " + self.name + " - processing URL")

            with self.output_lock:

                with open(f_name, "wb") as f:
                    for chunk in r.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            bytes_downloaded += len(chunk)

                            # Here we can pass to queue name of our process and % of download:
                            # And it seems that we need a prioritized queue ?
                            # self.queue.put_nowait([self.name, bytes_downloaded/total_length])

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
            worker = Downloader(self.queue, self.output_directory)
            worker.setDaemon(True)
            worker.start()
            self._progress[worker.name] = 0
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


"""
        This is an idea how to make async multiple progress bars output
        need to consider using prioritized queue maybe?

        def begin_download(self, add_url=None):

            if add_url is not None:
                dict(self.download_dict).clear()
                self.download_dict[os.urandom(5)] = add_url

            self.__start_workers()

            while any(i.is_alive() for i in self._workers):  
                time.sleep(0.1)
                while not self.queue.empty():
                    name, percent = self.queue.get()     <--Problem: we need to get() from queue only
                                                            progress related data but not urls
                    self._progress[name] = percent
                    self.print_progress()

            # wait for the queue to finish
            # self.queue.join()

            return

        def print_progress(progress):
            sys.stdout.write('\033[2J\033[H') #clear screen     <--Problem: we need to clear the screen 
                                                                   every time we want to draw
                                                                
                                                                <--Problem: current implementation of progress bar is 
                                                                not ideal, ideal would be to find a module that can 
                                                                behave good in this situation 
            for filename, percent in progress.items():
                bar = ('=' * int(percent * 20)).ljust(20)
                percent = int(percent * 100)
                sys.stdout.write("%s [%s] %s%%\n" % (filename, bar, percent))
            sys.stdout.flush()
"""




