from setuptools import setup
import os
import sys


def read(*names):
    values = dict()
    for name in names:
        if os.path.isfile(name):
            value = open(name).read()
        else:
            value = ''
        values[name] = value
    return values

long_description = """

%(README)s

""" % read('README')

setup(name='notirssi',
      version='1.0',
      description="Use libnotify / osx notification / growl / dbus over SSH to alert user for hilighted messages",
      long_description=long_description,
      classifiers=["Environment :: Console",
                   "Topic :: Communications :: Chat :: Internet Relay Chat",
                   "Environment :: MacOS X",
                   "Environment :: X11 Applications",
                   "Topic :: Text Editors :: Emacs"],
      keywords='ssh irc notifications growl libnotify irssi erc daemon',
      author='Matteo Bigoi',
      author_email='bigo at crisidev dot org',
      url='http://github.com/crisidev/notirssi',
      license='WTFPL',
      packages=['notirssi'],
      zip_safe=False,
      install_requires=[
          'argparse',
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      notirssi = notirssi.notirssi:main
      """,
      )

if "install" in sys.argv:
    print """
NotIRSSI is now installed!
You can configure how you want to connect to your IRC service:

cat >> ~/.ssh/config <EOF
    Host HOST
    PermitLocalCommand yes
    LocalCommand /path/to/bin/notossh
    RemoteForward PORT localhost:PORT
EOF

or simply notirssi --help

"""
