import os
import sys
import base64
import subprocess
import logging
from urlparse import urlparse
from data import _PNG, _ICON

Notify = None
if sys.platform == 'linux2':
    from gi.repository import Notify


class NotIRSSINotifierError(Exception):
    pass


class NotIRSSINotifier(object):
    PLATFORM_MAC = 'darwin'
    PLATFORM_LINUX = 'linux2'
    MAC_ICON = 'irssi.icns'
    LINUX_ICON = 'irssi.png'

    def __init__(self, args, workdir):
        self.workdir = workdir
        self._args = args
        self._notify = self._select_notify_function()
        self._log = logging.getLogger(__name__)

    def _select_notify_function(self):
        platform = sys.platform
        if platform == self.PLATFORM_MAC:
            return self._select_notify_function_mac()
        elif platform == self.PLATFORM_LINUX:
            self._write_icon(os.path.join(self.workdir, self.LINUX_ICON), _PNG)
            return self._select_notify_function_linux()
        else:
            raise NotIRSSINotifierError('unsupported platform {}'.format(platform))

    def _select_notify_function_mac(self):
        if self._args.notifier:
            if not os.path.isfile(self._args.notifier):
                raise NotIRSSINotifierError('{} not found'.format(self._args.notifier))
            return self._notify_terminal_notifier
        else:
            self._write_icon(os.path.join(self.workdir, self.MAC_ICON), _ICON)
            if not os.path.isfile(self._args.growl):
                raise NotIRSSINotifierError('{} not found'.format(self._args.notifier))
            return self._notify_growl

    def _select_notify_function_linux(self):
        if Notify:
            if self._args.verbose:
                self._log.debug('Initializing GTK Notify API')
            Notify.init("irssi")
            return self._notify_dbus
        else:
            if not os.path.isfile(self._args.notify):
                raise NotIRSSINotifierError('{} not found'.format(self._args.notify))
            return self._notify_cli

    def _write_icon(self, file_name, data):
        '''Decode the icon put at begining of the script.'''
        with open(file_name, 'w') as file_obj:
            file_obj.write(base64.b64decode(data))

    def _parse_message(self, message):
        nick, message = message.split('|x|')
        nick = nick.strip()
        message = message.lstrip('05')
        if self._args.verbose:
            self._log.debug('with label:{}, nick:{}, message:{}'.format(self._args.label, nick, message))
        nick = '{}: {}'.format(self._args.label, nick)
        return nick, message

    def _notify_growl(self, nick, message):
        growl_command = None
        if self._args.sticky:
            growl_command = [self._args.growl, '-s', '-n', 'Terminal', '--image', 'irssi.icns', '-m', nick, message]
        else:
            growl_command = [self._args.growl, '-n', 'Terminal', '--image', 'irssi.icns', '-m', nick, message]
        return subprocess.Popen(growl_command)

    def _notify_terminal_notifier(self, nick, message):
        url = urlparse(message)
        if url.scheme in ('http', 'https', 'ftp'):
            notifier_command = [self._args.notifier, '-sender', 'com.apple.iChat', '-open',
                                message.strip(), '-title', nick, '-message', message]
        else:
            notifier_command = [self._args.notifier, '-sender', 'com.apple.iChat', '-activate',
                                'com.googlecode.iterm2', '-title', nick, '-message', message]
        if self._args.verbose:
            self._log.debug(notifier_command)
            self._log.debug(url)
        return subprocess.Popen(notifier_command)

    def _notify_dbus(self, nick, message):
        n = Notify.Notification.new(nick, message, os.path.join(self.workdir, self.LINUX_ICON))
        n.set_category("im.received")
        n.show()
        return 0

    def _notify_cli(self, nick, message):
        return subprocess.Popen([self._args.notify, '-i', os.path.join(self.workdir, self.LINUX_ICON), '-t', '5000',
                                 nick, message])

    def notify(self, message):
        if self._args.verbose:
            self._log.debug('called {}'.format(self._notify))
        nick, message = self._parse_message(message)
        return self._notify(nick, message)
