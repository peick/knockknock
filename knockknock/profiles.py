# Copyright (c) 2009 Moxie Marlinspike
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import os
import socket

from profile import Profile


class Profiles:
    def __init__(self, directory):
        self._profiles = []

        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path) and os.listdir(path):
                self._profiles.append(Profile(path))


    def get_profile_for_port(self, port):
        assert type(port) == int
        for profile in self._profiles:
            if profile.knock_port == port:
                return profile


    def get_profile_for_name(self, name):
        for profile in self._profiles:
            if profile.name == name:
                return profile


    def get_profile_for_ip(self, ip):
        for profile in self._profiles:
            ips = profile.ip_addrs

            if ip in ips:
                return profile


    def resolve_names(self):
        for profile in self._profiles:
            address, alias, addrlist = socket.gethostbyname_ex(profile.name)

            profile.ip_addrs = addrlist


    def is_empty(self):
        return len(self._profiles) == 0

