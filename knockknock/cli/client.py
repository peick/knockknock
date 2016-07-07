#!/usr/bin/env python
__author__ = "Moxie Marlinspike"
__email__  = "moxie@thoughtcrime.org"
__license__= """
Copyright (c) 2009 Moxie Marlinspike <moxie@thoughtcrime.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the
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
import struct
import subprocess
import sys

from knockknock.profile import Profile


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='~/.knockknock',
                        help='Defaults to ~/.knockknock')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('host', help='Address of the knockknock server')

    args = parser.parse_args()
    args.config_dir = os.path.expanduser(args.config_dir)

    return (args.port, args.host, args.config_dir)


def _get_profile(host, config_dir):
    profiles_dir = os.path.join(config_dir, 'profiles')
    hostdir      = os.path.join(profiles_dir, host)

    if not os.path.isdir(config_dir):
        print "Error: you need to setup your profiles in %s" % (config_dir, )
        sys.exit(2)

    if not os.path.isdir(hostdir):
        print 'Error: profile for host %s not found at %s' % (host, hostdir)
        sys.exit(2)

    return Profile(hostdir)


def _verify_permissions():
    if os.getuid() != 0:
        print 'Sorry, you must be root to run this.'
        sys.exit(2)


def _exists_in_path(command):
    def is_executable(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, command)
        if is_executable(exe_file):
            return exe_file


def main():
    (port, host, config_dir) = _parse_arguments()
    _verify_permissions()

    profile     = _get_profile(host, config_dir)
    port        = struct.pack('!H', port)
    packet_data = profile.encrypt(port)
    knock_port  = profile.knock_port

    (id_field, seq_field, ack_field, win_field) = struct.unpack('!HIIH', packet_data)

    hping = _exists_in_path("hping3")

    if not hping:
        print "Error, you must install hping3 first."
        sys.exit(2)

    command = [hping, "-q",
               "-S", "-c", "1",
               "-p", '%d' % knock_port,
               "-N", '%d' % id_field,
               "-w", '%d' % win_field,
               "-M", '%d' % seq_field,
               "-L", '%d' % ack_field,
               host]

    try:
        subprocess.call(command,
                        shell=False,
                        stdout=open('/dev/null', 'w'))
        print 'Knock sent.'

    except OSError:
        print "Error: Do you have hping3 installed?"
        sys.exit(3)


if __name__ == '__main__':
    main()

