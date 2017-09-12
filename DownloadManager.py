from queue import Queue
import Downloader


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
            t = Downloader.Downloader(queue, self.output_directory)
            t.setDaemon(True)
            t.start()

        # Load the queue from download dict

        for linkname in self.download_dict:
            # print uri
            queue.put(self.download_dict[linkname])

        # wait for the queue to finish
        queue.join()

        return


