import sys
from getopt import getopt, GetoptError
import json

import time

import DownloadManager
import os
import ClipboardWatch as watch


class Factory:
    def __init__(self, output_directory, input_file, flist):
        self._input_file = input_file
        self._fList = flist
        self._output_directory = output_directory
        self._max_threads = 5

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
        worker = DownloadManager.DownloadManager(output_directory, None)
        watcher = watch.ClipboardWatcher(watch.is_downloadable_url, worker, 5.)
        watcher.start()

        while True:
            try:
                print('----------------PyDownload---------------')
                print('          Watching your clipboard...     ')
                print('-----------------------------------------')
                time.sleep(10)
            except KeyboardInterrupt:
                watcher.stop()
                break


def init(argv):
    """print('----------PyDownload---------------')
print('------------------------------------')
print('JSON file:             ', input_file)
print('Output Directory:      ', output_directory)
print('File list:             ', f_list)
print('------------------------------------')

# Building a dict with download urls
download_dic = {}

# If the input passed as file input parse it as JSON
if input_file is not None:
    fp = open(input_file)
    url_list = json.load(fp)
    for url in url_list:
        download_dic[url['link_name']] = url['link_address']

# Add in any additional files contained in the flist variable
if f_list is not None and type(f_list) is []:
    for f in f_list:
        download_dic[os.path.basename(f)] = f

elif f_list is not None:
    direct_link = f_list

download_manager = DownloadManager.DownloadManager(download_dic, output_directory, 5)

if direct_link.__len__() is not 0:
    download_manager.begin_download(direct_link)
else:
    # If there are no URLs to download then exit now, nothing to do!
    if len(download_dic) is 0:
        print("* No URLs to download, got the usage right?")
        print("USAGE: " + help)
        sys.exit(2)

    download_manager.begin_download()"""


class Initializer:
    def __init__(self, options, args, output_directory):
        self._options = options
        self._args = args
        self._output_directory = output_directory
        self._inputFile = None
        self._fList = None

    def process(self):
        for opt, arg in self._options:
            if self._options is None or '--watch' in self._options:
                Factory.start_watching(self._output_directory)
                return
            if opt == '-h':
                print(help)
                sys.exit(2)
            elif opt in ("-i", "--ifile"):
                self._inputFile = arg
            elif opt in ("-f", "--flist"):
                if ',' in arg:
                    self._fList = [i for i in arg.slit(',')]
                else:
                    self._fList = arg

                    # TODO: continue to build dic and pass it to factory
        return Factory(self._output_directory, self._inputFile, self._fList)


def main(argv):
    help = """PyDownload.py ./output_directory/ [optional: --watch] -i(--ifile) <JSON input_file>  -f(--flist) <url1,url2,url3...>
    
    """
    watch_mode = """
    -----------------------------PyDownload-----------------------------\n
    No arguments were specified. Application will turn into 'watch' mode\n
    It will try to catch all urls from clipboard and download them.\n
    Are you sure to enter 'watch' mode? y/n \n
    --------------------------------------------------------------------"""

    try:
        opts, args = getopt(argv[1:], "hi:f:", ["ifile=", "flist=", "watch"])
    except GetoptError:
        print(help)
        sys.exit(2)

    # save an output dict
    if len(argv[0]) > 0 and not argv[0].startswith('-'):
        output_directory = argv[0]
        try:
            os.stat(output_directory)
        except OSError:
            print('ERROR: Path format is incorrect: Please specify correct path format')
            sys.exit(2)
    else:
        print(help)
        sys.exit(2)

    Initializer(opts, args, output_directory).process()


if __name__ == "__main__":
    main(sys.argv[1:])
