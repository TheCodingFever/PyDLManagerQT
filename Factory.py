import sys
import json
import DownloadManager
import os
import click
import RegexUtility


class Factory:
    def __init__(self, output_directory, input_file, flist, is_watch=False):
        self._input_file = input_file
        self._fList = flist
        self._output_directory = output_directory
        self._max_threads = 5
        self._is_watch = is_watch

    @property
    def is_watch(self):
        return self._is_watch

    def __build_urls(self):
        # Init dictionary
        download_dic = {}

        try:
            # If the input passed as file input parse it as JSON
            if self._input_file is not None:
                fp = open(self._input_file)
                url_list = json.load(fp)
                for url in url_list:
                    download_dic[url['link_name']] = url['link_address']
        except click.ClickException('JSON %s structure is not as expected. See --help' % self._input_file):
            sys.exit(2)

        if self._fList is not None and self._fList:
            # Add in any additional files contained in the flist variable
            if len(self._fList) > 0:
                for f in self._fList:
                    if RegexUtility.is_downloadable_url(f):
                        download_dic[os.path.basename(f)] = f
            else:
                click.echo('No urls to work with were found!')
                click.echo('Quiting the program')
                sys.exit(2)

        return download_dic

    def prepare_data(self):
        targets_dictionary = {}

        if not self._is_watch:
            targets_dictionary = self.__build_urls()

        return DownloadManager.DownloadManager(self._output_directory, targets_dictionary)


class Initializer:
    def __init__(self, f_list, i_file, output_directory, is_watch=False):
        self._fList = f_list
        self._iFile = i_file
        self._output_directory = output_directory
        self._isWatch = is_watch

    def process(self):

        if self._isWatch:
            self.__watch_interactive()

        return Factory(self._output_directory, self._iFile, self._fList, self._isWatch).prepare_data()

    @staticmethod
    def __watch_interactive():

        watch_mode = """
-----------------------------PyDownload-----------------------------
No urls to download were specified or --watch mode selected.
Application will turn into 'watch' mode
It will try to catch all urls from clipboard and download them.
Are you sure to enter 'watch' mode?    
--------------------------------------------------------------------\n"""

        if click.confirm(watch_mode, abort=True):
            return
        else:
            click.echo('Thanks for checking it out! Bye!')
