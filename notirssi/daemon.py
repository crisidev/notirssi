import os
import sys
import socket
import signal
import resource
import shutil
import logging
import tempfile

from notifier import NotIRSSINotifier


class NotIRSSIDaemonError(Exception):
    pass


class NotIRSSIDaemon(object):
    MAXFD = 1024
    UMASK = 766

    def __init__(self, args):
        self._args = args
        self.daemon_name = 'notirssi.{}'.format(self._args.label.lower())
        self.workdir_file = os.path.join('/tmp', '{}.dir'.format(self.daemon_name))
        self.workdir = self._setup_workdir()
        self._log = self._setup_logging(level=self._args.log_level, console=self._args.foreground)
        self._redirect_to = os.devnull
        self.pid_file = os.path.join('/tmp', '{}.pid'.format(self.daemon_name))
        self._log.info('daemon: {}, workdir: {}'.format(self.daemon_name, self.workdir))

    def _write_tmp_file(self, file_name, content):
        with open(file_name, 'w') as file_obj:
            file_obj.write(str(content))

    def _read_tmp_file(self, file_name):
        content = None
        try:
            with open(file_name, 'r') as file_obj:
                content = file_obj.read()
            if content:
                return content
            else:
                raise NotIRSSIDaemonError('empty file {}... exiting...'.format(file_name))
        except IOError:
                raise NotIRSSIDaemonError('file {} not found... exiting...'.format(file_name))

    def _setup_workdir(self):
        workdir = None
        try:
            workdir = self._read_tmp_file(self.workdir_file)
        except NotIRSSIDaemonError:
            workdir = tempfile.mkdtemp()
            self._write_tmp_file(self.workdir_file, workdir)
        return workdir

    def _setup_logging(self, level=logging.INFO, console=False):
        log_path = os.path.join(self.workdir, '{}.log'.format(self.daemon_name))
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        logger = logging.getLogger(self.daemon_name)
        logger.setLevel(level)
        logger.addHandler(file_handler)
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
        return logger

    def _spawn_daemon(self):
        """Detach a process from the controlling terminal and run it in the
        background as a daemon.
        """
        self._fork()
        self._cleanup()
        self._dup()
        return 0

    def _kill_daemon(self, signum, stack):
        """Remove the PID file and exit with return code 1"""
        os.unlink(self.pid_file)
        os.unlink(self.workdir_file)
        sys.exit(1)

    def _fork(self):
        try:
            pid = os.fork()
        except OSError as e:
            raise NotIRSSIDaemonError('{} [{}]'.format(e.strerror, e.errno))
        if pid == 0:  # The first child.
            os.setsid()
            try:
                pid = os.fork()  # Fork a second child.
            except OSError as e:
                raise NotIRSSIDaemonError('{} [{}]'.format(e.strerror, e.errno))
            if pid == 0:  # The second child.
                os.chdir(self.workdir)
                os.umask(self.UMASK)
            else:
                os._exit(0)  # Exit parent (the first child) of the second child.
        else:
            os._exit(0)  # Exit parent of the first child.

    def _cleanup(self):
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = self.MAXFD
        # Iterate through and close all file descriptors.
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:  # ERROR, fd wasn't open to begin with (ignored)
                pass

    def _dup(self):
        # This call to open is guaranteed to return the lowest file descriptor,
        # which will be 0 (stdin), since it was closed above.
        os.open(self._redirect_to, os.O_RDWR)  # standard input (0)
        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)  # standard output (1)
        os.dup2(0, 2)  # standard error (2)

    def _check_pid(self, pid):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(int(pid), 0)
        except OSError:
            return False
        return True

    def _check_if_daemon_exists(self):
        if os.path.isfile(self.pid_file):
            pid = self._read_tmp_file(self.pid_file)
            if self._check_pid(pid):
                return True
            return False

    def _bind_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self._args.host, self._args.port))
        sock.listen(1)
        if self._args.verbose:
            self._log.debug('listening on {}:{}...'.format(str(self._args.host), str(self._args.port)))
        return sock

    def _handle_run_mode(self):
        signal.signal(signal.SIGTERM, self._kill_daemon)
        if not self._args.foreground:
            if self._args.verbose:
                self._log.debug('starting server as daemon...')
            self._spawn_daemon()
            self._write_tmp_file(self.pid_file, os.getpid())
        else:
            self._log.info('starting server in foreground mode...')

    def _daemon_loop(self, sock):
        while True:
            conn, addr = sock.accept()
            while 1:
                data = conn.recv(1024)
                if not data:
                    break
                if self._args.verbose:
                    self._log.debug('RCPT: {}'.format(str(data)))
                self.notifier.notify(data)
            conn.close()

    def start(self):
        self.notifier = NotIRSSINotifier(args, self.workdir)
        self._log.info('starting daemon {}'.format(self.daemon_name))
        if self._check_if_daemon_exists():
            raise NotIRSSIDaemonError('daemon is already running... exiting.')
        self._handle_run_mode()
        sock = self._bind_socket()
        self._daemon_loop(sock)
        return 0

    def stop(self):
        if not os.path.isfile(self.pid_file):
            raise NotIRSSIDaemonError('nothing to stop. exiting...')
        try:
            pid = self._read_tmp_file(self.pid_file)
            os.kill(int(pid), 9)
            self._kill_daemon(None, None)
        except ValueError:
            raise NotIRSSIDaemonError('invalid PID file. exiting...')
        except OSError:
            raise NotIRSSIDaemonError('invalid PID: {}. process has already exited. exiting...'.format(pid))
        finally:
            shutil.rmtree(self.workdir)
            self._log.info('daemon {} killed'.format(self.daemon_name))
        return 0

    def check(self):
        if self._check_if_daemon_exists():
            self._log.debug('daemon {}, pid: {}, work_dir:{}'.format(self.daemon_name,
                                                                     self._read_tmp_file(self.pid_file),
                                                                     self._read_tmp_file(self.workdir_file)))
        else:
            self._log.debug('daemon {} not running'.format(self.daemon_name))
        return 0
