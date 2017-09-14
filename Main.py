import sys
import os
from getopt import getopt, GetoptError
from Core import Initializer


help = """
PyDownload.py ./output_directory/ [optional: --watch] -i(--ifile) <JSON input_file>  -f(--flist) <url1,url2,url3...>

"""


def main(argv):
    try:
        opts, args = getopt(argv[1:], "hi:f:", ["ifile=", "flist=", "watch"])
    except GetoptError:
        print(help)
        sys.exit(2)

    try:
        # save and validate an output directory
        if len(argv[0]) > 0 and not argv[0].startswith('-') or argv[0].startswith('--'):
            output_directory = argv[0]
            try:
                os.stat(output_directory)
            except OSError:
                print('ERROR: Path format "%s" is incorrect. Please specify correct path format' % output_directory)
                sys.exit(2)
        else:
            print('No required arguments were passed: "Download Folder"')
            sys.exit(2)
    except IndexError:
        print('No required arguments were passed: "Download Folder"')
        sys.exit(2)

    download_manager = Initializer(opts, args, output_directory).process()
    if download_manager is not None:
        download_manager.begin_download()
    else:
        sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
