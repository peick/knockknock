#!/usr/bin/env python
import argparse
import errno
import os
import sys

import knockknock.daemonize
from knockknock.cli.log_setup import setup_logging
from knockknock.knock_watcher import KnockWatcher
from knockknock.log_file import LogFile
from knockknock.port_opener import PortOpener
from knockknock.profiles import Profiles


DAEMON_DIR = '/etc/knockknock'


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default=DAEMON_DIR,
                        help='Configuration directory containing profiles. ' +
                             'Defaults to %s' % DAEMON_DIR)
    parser.add_argument('-f', '--foreground',
                        action='store_true',
                        help='Run in foreground.')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    return args


def _check_privileges():
    if os.geteuid() == 0:
        print "You are running knockknock-daemon as root which is not recommend."
    else:
        try:
            open('/var/log/kern.log')
        except IOError as error:
            if error.errno == errno.EACCES:
                print "User %s does not have permissions to read /var/log/kern.log"
                sys.exit(3)


def _check_configuration(config_dir):
    if not os.path.isdir(config_dir):
        print "%s directory does not exist. You need to setup your profiles first." % (config_dir, )


def _handle_firewall(input):
    port_opener = PortOpener(input)
    port_opener.wait_for_requests()


def _handle_knocks(profiles):
    log_file      = LogFile('/var/log/kern.log')
    port_opener   = PortOpener()
    knock_watcher = KnockWatcher(log_file, profiles, port_opener)

    knock_watcher.tail_and_process()


def main():
    args = _parse_arguments()
    setup_logging(args.verbose)

    _check_privileges()
    _check_configuration(args.config_dir)

    profiles = Profiles(args.config_dir)

    if profiles.is_empty():
        print 'WARNING: Running knockknock-daemon without any active profiles.'

    if not args.foreground:
        knockknock.daemonize.createDaemon()

    _handle_knocks(profiles)


if __name__ == '__main__':
    main()

