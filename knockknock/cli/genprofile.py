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
import sys

from knockknock.profiles import Profiles
from knockknock.profile  import Profile


DAEMON_DIR   = '/etc/knockknock.d'
PROFILES_DIR = os.path.join(DAEMON_DIR, 'profiles')


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', metavar='KNOCK_PORT', type=int)
    parser.add_argument('profile', metavar='PROFILE_NAME')
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='/etc/knocknock.d',
                        help='Defaults to /etc/knockknock.d')

    args = parser.parse_args()
    args.config_dir = os.path.expanduser(args.config_dir)

    return (args.port, args.profile, args.config_dir)


def _check_profile(profile_dir):
    if os.path.isdir(profile_dir) and os.listdir(profile_dir):
        print "Profile already exists: %s" % (profile_dir, )
        sys.exit(1)


def _check_port_conflict(profiles_dir, knock_port):
    if not os.path.isdir(profiles_dir):
        return

    profiles         = Profiles(profiles_dir)
    matching_profile = profiles.get_profile_for_port(knock_port)

    if matching_profile:
        print "A profile already exists for knock port %d at %s" % (knock_port, matching_profile.directory)
        sys.exit(1)


def _create_directory(profile_dir):
    if not os.path.isdir(profile_dir):
        os.makedirs(profile_dir)


def main():
    (knock_port, profile_name, config_dir) = _parse_arguments()

    profiles_dir = os.path.join(config_dir, 'profiles')
    profile_dir  = os.path.join(profiles_dir, profile_name)

    _check_profile(profile_dir)
    _check_port_conflict(profiles_dir, knock_port)
    _create_directory(profile_dir)

    random     = open('/dev/urandom', 'rb')
    cipher_key = random.read(16)
    mac_key    = random.read(16)
    counter    = 0

    profile = Profile(profile_dir, cipher_key, mac_key, counter, knock_port)
    profile.serialize()
    random.close()

    print "Keys successfully generated in %s" % (profile_dir, )


if __name__ == '__main__':
    main()
