import sys
import json
import time
import DownloadManager
import os
import ClipboardWatcher as Watch
import click


class Factory:
    def __init__(self, output_directory, input_file, flist):
        self._input_file = input_file
        self._fList = flist
        self._output_directory = output_directory
        self._max_threads = 5

    @property
    def input_file(self):
        return self._input_file

    @property
    def max_threads(self):
        return self._max_threads

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value

    @staticmethod
    def start_watching(output_directory):
        worker = DownloadManager.DownloadManager(output_directory, None, None)
        watcher = Watch.ClipboardWatcher(Watch.is_downloadable_url, worker, 5.)
        watcher.setDaemon(True)
        watcher.start()

        print('----------------PyDownload---------------')
        print('          Watching your clipboard...     ')
        print('           Press Any Key to exit         ')
        print('-----------------------------------------\n')

        choice = ''
        while choice is '':
            try:
                time.sleep(10)
                choice = input()
            except KeyboardInterrupt:
                watcher.stop()
                break

    def __build_urls(self):
        # Init dictionary
        download_dic = {}

        # TODO: URL VALIDATION NEEDED BEFORE WE COMPILE THE DICTIONARY!

        # If the input passed as file input parse it as JSON
        if self._input_file is not None:
            fp = open(self._input_file)
            url_list = json.load(fp)
            for url in url_list:
                download_dic[url['link_name']] = url['link_address']

        if self._fList is not None:
            # Add in any additional files contained in the flist variable
            if len(self._fList) > 0:
                for f in self._fList:
                    download_dic[os.path.basename(f)] = f
            else:
                print('No urls to work with were found!')
                print('Quiting the program')
                sys.exit(2)

        return download_dic

    def prepare_data(self):

        download_dic = self.__build_urls()

        return DownloadManager.DownloadManager(self.output_directory, download_dic)


class Initializer:
    def __init__(self, f_list, i_file, output_directory, is_watch=False):
        self._fList = f_list
        self._iFile = i_file
        self._output_directory = output_directory
        self._isWatch = is_watch

    def process(self):

        if self._isWatch:
            self.__watch_interactive()
            Factory.start_watching(self._output_directory)
            return None

        return Factory(self._output_directory, self._iFile, self._fList).prepare_data()

    @staticmethod
    def __watch_interactive():

        watch_mode = """
        -----------------------------PyDownload-----------------------------\n
        No arguments were specified or --watch mode selected.\n
        Application will turn into 'watch' mode\n
        It will try to catch all urls from clipboard and download them.\n
        Are you sure to enter 'watch' mode?    \n
        --------------------------------------------------------------------\n"""

        if click.confirm(watch_mode, abort=True):
            return
        else:
            click.echo('Thanks for checking it out! Bye!')
