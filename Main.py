from Core import Initializer
import click

@click.command()
@click.argument('output_directory', type=click.Path(exists=True))
@click.option('--ifile', '-i', default=None, type=click.Path(), help='JSON file with structure as following: '
                                                                     '"link_name": "value", "link_address": "value"')
@click.option('--url', '-u', multiple=True, type=click.Path(), default=None,
              help='Provide a List of an additional urls to download')
@click.option('--watch', is_flag=True,
              help='Enables watch mode: application will watch for all links in clipboard and tries to download them')
def main(output_directory, ifile, url, watch):

    """ This is a PyDownload lite, console version of multi-threading auto downloader.
    Current features: ability to download files either from single links provided as arguments
    as well as from multiple links stored in json file. Ability to run into 'watch mode' where program
    will try to catch all appropriate links from clipboard and download files. v.0.0.1a """

    if not watch and not url and ifile is None:
        watch = True

    download_manager = Initializer(url, ifile, output_directory, watch).process()

    if watch:
        download_manager.start_watching()

    else:
        download_manager.begin_download()


if __name__ == "__main__":
    main()
