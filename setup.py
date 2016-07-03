#from distutils.core import setup
import sys
from setuptools import setup


if sys.version_info >= (2,6):
    install_requires = []
else:
    install_requires = ['argparse']


setup(name         = 'knockknock',
      version      = '0.9a1',
      description  = 'A cryptographic single-packet port-knocker.',
      author       = 'Moxie Marlinspike',
      author_email = 'moxie@thoughtcrime.org',
      url          = 'http://www.thoughtcrime.org/software/knockknock/',
      license      = 'GPL',
      packages     = ["knockknock", "knockknock.proxy", "knockknock.cli"],
      install_requires = [
          'pycrypto'
      ] + install_requires,
      #data_files   = [("", ["minimal-firewall.sh"]),
      #                ('share/knockknock', ['README', 'INSTALL', 'COPYING']),
      #                ('/etc/knockknock.d/', ['config'])],
      entry_points = {
          'console_scripts': [
              'knockknock-daemon     = knockknock.cli.daemon:main',
              'knockknock-genprofile = knockknock.cli.genprofile:main',
              'knockknock-proxy      = knockknock.cli.proxy:main',
              'knockknock            = knockknock.cli.client:main'
          ]
      }
)

