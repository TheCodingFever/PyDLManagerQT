from setuptools import setup, find_packages

long_description = \
    """ This is a PyDownload lite, console version of multi-threading auto downloader.
    Current features: ability to download files either from single links provided as arguments
    as well as from multiple links stored in json file. Ability to run into 'watch mode' where program
    will try to catch all appropriate links from clipboard and download files. v.0.0.1a """


setup(
    name='PyDLManagerQT',
    version='0.0.1a',
    packages=[find_packages()],
    install_requires=['click', 'requests', 'progressbar2', 'pyperclip'],
    url='https://github.com/MixolydianBY/PyDLManagerQT.git',
    license='MIT',
    author='Mixolydian',
    author_email='',
    description=long_description
)
