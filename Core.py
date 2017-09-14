import sys
import json
import time
import DownloadManager
import os
import ClipboardWatcher as watch

help = """
PyDownload.py ./output_directory/ [optional: --watch] -i(--ifile) <JSON input_file>  -f(--flist) <url1,url2,url3...>

"""


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
        watcher = watch.ClipboardWatcher(watch.is_downloadable_url, worker, 5.)
        watcher.setDaemon(True)
        watcher.start()

        print('----------------PyDownload---------------')
        print('          Watching your clipboard...     ')
        print('           Press Any Key to exit         ')
        print('-----------------------------------------\n')

        choice = ''
        while choice is '':
            try:
                #time.sleep(10)
                choice = input()
            except KeyboardInterrupt:
                watcher.stop()
                break


    def __build_urls(self):
        # Init dictionary
        download_dic = {}
        direct_link = None

        # If the input passed as file input parse it as JSON
        if self._input_file is not None:
            fp = open(self._input_file)
            url_list = json.load(fp)
            for url in url_list:
                download_dic[url['link_name']] = url['link_address']

        # Add in any additional files contained in the flist variable
        if self._fList is not None and type(self._fList) is []:
            for f in self._fList:
                download_dic[os.path.basename(f)] = f
        elif self._fList is not None:
            direct_link = self._fList
        else:
            print('No urls to work with were found!')
            print('Quiting the program')
            sys.exit(2)

        return download_dic, direct_link

    def prepare_data(self):

        download_dic, direct_link = self.__build_urls()

        return DownloadManager.DownloadManager(download_dic, self.output_directory, 5)


class Initializer:
    def __init__(self, options, args, output_directory):
        self._options = options
        self._args = args
        self._output_directory = output_directory
        self._inputFile = None
        self._fList = None

    def process(self):

        if not self._options or '--watch' in self._options:
            self.__watch_interactive()
            Factory.start_watching(self._output_directory)
            return None

        for opt, arg in self._options:
            if '-h' in self._options:
                print(help)
                sys.exit(2)
            elif opt in ("-i", "--ifile"):
                self._inputFile = arg
            elif opt in ("-f", "--flist"):
                if ',' in arg:
                    self._fList = [i for i in arg.slit(',')]
                else:
                    self._fList = arg

        return Factory(self._output_directory, self._inputFile, self._fList).prepare_data()

    def __watch_interactive(self):

        watch_mode = """
        -----------------------------PyDownload-----------------------------\n
        No arguments were specified or --watch mode selected.\n
        Application will turn into 'watch' mode\n
        It will try to catch all urls from clipboard and download them.\n
        Are you sure to enter 'watch' mode? y/n \n
        --------------------------------------------------------------------\n"""

        while True:
            print(watch_mode)
            choice = input('>')
            if choice is 'y':
                break
            else:
                print('Thanks for trying it out! Bye!')
                sys.exit(0)
