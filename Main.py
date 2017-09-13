import sys
from getopt import getopt, GetoptError
import json
import DownloadManager
import os


def main(argv):
    input_file = None
    f_list = None
    help = 'PyDownload.py ./output_directory/ -i <JSON input_file>  -f <url1,url2,url3...>'
    try:
        opts, args = getopt(argv[1:], "hi:f:", ["ifile=", "flist="])
    except GetoptError:
        print(help)
        sys.exit(2)

    # save an output dict
    if len(argv[0]) > 0 and not argv[0].startswith('-'):
        output_directory = argv[0]
    else:
        print(help)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit(2)
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-f", "--flist"):
            if ',' in arg:
                f_list = [i for i in arg.slit(',')]
            else:
                f_list = arg

    print('----------PyDownload---------------')
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

        download_manager.begin_download()


if __name__ == "__main__":
    main(sys.argv[1:])
