#!/usr/bin/env python
"""knockknock-daemon implements Moxie Marlinspike's port knocking protocol."""

__author__ = "Moxie Marlinspike"
__email__  = "moxie@thoughtcrime.org"
__license__= """
Copyright (c) 2009 Moxie Marlinspike <moxie@thoughtcrime.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""

import argparse
import os
import sys
import pwd
import grp

import knockknock.daemonize
from knockknock.log_file import LogFile
from knockknock.profiles import Profiles
from knockknock.port_opener import PortOpener
from knockknock.daemon_configuration import DaemonConfiguration
from knockknock.knock_watcher import KnockWatcher


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='/etc/knocknock.d')
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
    profiles_dir = os.path.join(config_dir, 'profiles')

    if not os.path.isdir(config_dir):
        print "%s does not exist.  You need to setup your profiles first.." % (config_dir, )
        sys.exit(3)

    if not os.path.isdir(profiles_dir):
        print "%s does not exist.  You need to setup your profiles first..." % (profiles_dir, )
        sys.exit(3)


def _drop_privileges():
    nobody = pwd.getpwnam('nobody')
    adm    = grp.getgrnam('adm')

    os.setgroups([adm.gr_gid])
    os.setgid(adm.gr_gid)
    os.setuid(nobody.pw_uid)


def _handle_firewall(input, config):
    port_opener = PortOpener(input, config.delay)
    port_opener.wait_for_requests()


def _handle_knocks(output, profiles, config):
    _drop_privileges()

    log_file      = LogFile('/var/log/kern.log')
    port_opener   = PortOpener(output, config.delay)
    knock_watcher = KnockWatcher(config, log_file, profiles, port_opener)

    knock_watcher.tail_and_process()


def main():
    (config_dir, foreground) = _parse_arguments()

    _check_privileges()
    _check_configuration(config_dir)

    profiles = Profiles(os.path.join(config_dir, 'profiles'))
    config   = DaemonConfiguration(os.path.join(config_dir, 'config'))

    if profiles.is_empty():
        print 'WARNING: Running knockknock-daemon without any active profiles.'

    if not foreground:
        knockknock.daemonize.createDaemon()

    input, output = os.pipe()
    pid           = os.fork()

    if pid:
        os.close(input)
        _handle_knocks(os.fdopen(output, 'w'), profiles, config)
    else:
        os.close(output)
        _handle_firewall(os.fdopen(input, 'r'), config)


if __name__ == '__main__':
    main()

