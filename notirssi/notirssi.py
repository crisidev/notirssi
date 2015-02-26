#!/usr/bin/env python

# Echo server program
import sys
import argparse
import logging

from notifier import NotIRSSINotifierError
from daemon import NotIRSSIDaemon, NotIRSSIDaemonError

# Informations
__idea__ = 'Bernard `Guyzmo` Pratz - http://github.com/guyzmo/notossh'
__author__ = 'Matteo Bigoi'
__credits__ = ["Matteo Bigoi", "Bernard `Guyzmo` Pratz", "Charles `doublerebel` Philips",
               "Rui Abreu Ferreira", "Cooper Ry Lees", "Kevin Mershon"]
__email__ = 'bigo at crisidev dot org'
__status__ = "Development"

__NAME__ = 'notirssi'
__version__ = '1.0'
__maintainer__ = 'Matteo Bigoi'
__description__ = 'Use libnotify / osx notification / growl / dbus over SSH to alert user for hilighted messages'
__license__ = 'WTF Public License <http://sam.zoy.org/wtfpl/>'
__url__ = 'http://github.com/crisidev/notirssi'

# Constants


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='IRSSI Notify Listener',
                                     epilog='By {} with patches from {}'.format(__author__, ', '.join(__credits__[1:])))

    sp = parser.add_subparsers()

    sp.add_parser('start', help='Starts the service').set_defaults(command='start')
    sp.add_parser('stop', help='Stops the service').set_defaults(command='stop')
    sp.add_parser('check', help='Checks the service').set_defaults(command='check')

    parser.add_argument("-f",
                        "--foreground",
                        dest="foreground",
                        action="store_true",
                        help='Make the notifications stick')
    parser.add_argument("-S",
                        "--sticky",
                        dest="sticky",
                        action="store_true",
                        help='Make the notifications stick')
    parser.add_argument("-V",
                        "--verbose",
                        dest="verbose",
                        action="store_true",
                        help='Make the listener verbose')
    parser.add_argument('-H', '--host',
                        dest='host',
                        action='store',
                        default='localhost',
                        help='Host to listen on')
    parser.add_argument('-P', '--port',
                        dest='port',
                        action='store',
                        default=4222,
                        type=int,
                        help='Port to listen on')
    parser.add_argument('-G', '--with-growl',
                        dest='growl',
                        action='store',
                        default='/usr/local/bin/growlnotify',
                        help='Path to growl executable')
    parser.add_argument('-N', '--with-notify',
                        dest='notify',
                        action='store',
                        default='/usr/bin/notify-send',
                        help='Path to notify executable'),
    parser.add_argument('-T', '--with-terminal-notifier',
                        dest='notifier',
                        action='store',
                        help='Path to terminal-notifier executable')
    parser.add_argument('-L', '--label',
                        dest='label',
                        action='store',
                        default='IRC',
                        help='Label for terminal-notifier')

    args = parser.parse_args()

    if args.verbose:
        args.log_level = logging.DEBUG
    else:
        args.log_level = logging.INFO

    if args.command == 'check':
        args.foreground = True

    return args


def main():
    args = parse_args()
    try:
        n = NotIRSSIDaemon(args)
        if args.command == 'start':
            ret = n.start()
        elif args.command == 'stop':
            ret = n.stop()
        elif args.command == 'check':
            ret = n.check()
    except (NotIRSSIDaemonError, NotIRSSINotifierError) as e:
        print e.message
        sys.exit(1)
    else:
        sys.exit(ret)


if __name__ == '__main__':
    main()
