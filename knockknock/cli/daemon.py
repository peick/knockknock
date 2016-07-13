#!/usr/bin/env python
import argparse
import os
import sys
import pwd
import grp

import knockknock.daemonize
from knockknock.knock_watcher import KnockWatcher
from knockknock.log_file import LogFile
from knockknock.port_opener import PortOpener
from knockknock.profiles import Profiles


DAEMON_DIR = '/etc/knockknock'


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default=DAEMON_DIR)
    parser.add_argument('-f', '--foreground',
                        action='store_true',
                        help='Run in foreground.')

    args = parser.parse_args()

    return (args.config_dir, args.foreground)


def _check_privileges():
    if not os.geteuid() == 0:
        print "Sorry, you have to run knockknock-daemon as root."
        sys.exit(3)


def _check_configuration(config_dir):
    if not os.path.isdir(config_dir):
        print "%s directory does not exist. You need to setup your profiles first." % (config_dir, )


def _drop_privileges():
    nobody = pwd.getpwnam('nobody')
    adm    = grp.getgrnam('adm')

    os.setgroups([adm.gr_gid])
    os.setgid(adm.gr_gid)
    os.setuid(nobody.pw_uid)


def _handle_firewall(input):
    port_opener = PortOpener(input)
    port_opener.wait_for_requests()


def _handle_knocks(output, profiles):
    _drop_privileges()

    log_file      = LogFile('/var/log/kern.log')
    port_opener   = PortOpener(output)
    knock_watcher = KnockWatcher(log_file, profiles, port_opener)

    knock_watcher.tail_and_process()


def main():
    (config_dir, foreground) = _parse_arguments()

    _check_privileges()
    _check_configuration(config_dir)

    profiles = Profiles(config_dir)

    if profiles.is_empty():
        print 'WARNING: Running knockknock-daemon without any active profiles.'

    if not foreground:
        knockknock.daemonize.createDaemon()

    input, output = os.pipe()
    pid           = os.fork()

    if pid:
        os.close(input)
        _handle_knocks(os.fdopen(output, 'w'), profiles)
    else:
        os.close(output)
        _handle_firewall(os.fdopen(input, 'r'))


if __name__ == '__main__':
    main()

