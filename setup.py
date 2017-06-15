

from distutils.core import setup


setup(
    name='snaptime',
    packages=['snaptime'],  # this must be the same as the name above
    version='0.2.4',
    description='Transform timestamps with a simple DSL',  # think of including iconic '+1d@d' or similar
    install_requires=['python-dateutil', 'pytz'],
    author='Philipp Hitzler',
    author_email='phj.hitzler@gmail.com',
    url='https://github.com/zartstrom/snaptime',  # use the URL to the github repo
    download_url='https://github.com/zartstrom/snaptime/tarball/0.2.4',
    keywords=['snap', 'datetime', 'date', 'truncate', 'transform'],
    classifiers=[],
)
