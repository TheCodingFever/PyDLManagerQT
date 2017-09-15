import sys
from Core import Initializer
import click


@click.command(help='azazaza')
@click.argument('output_directory', type=click.Path(exists=True))
@click.option('--ifile', '-i', default=None, type=click.Path(), help='Path to your json file with links to download')
@click.option('--url', '-u', multiple=True, type=str, default=None,
              help='Provide a List of an additional urls to download')
@click.option('--watch', is_flag=True,
              help='Enables watch mode: application will watch for all links in clipboard and tries to download them')
def main(output_directory, ifile, url, watch):
    if not watch and url is None and ifile is None:
        print('Please specify at least one Url to download unless you are not using --watch option')
        click.help_option()
        sys.exit(0)

    download_manager = Initializer(url, ifile, output_directory, watch).process()
    if download_manager is not None:
        download_manager.begin_download()
    else:
        sys.exit(0)



if __name__ == "__main__":
    main()
