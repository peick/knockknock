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

import struct


_INTEGER_KEYS = set(['DPT', 'ID', 'SEQ', 'ACK', 'WINDOW'])


class LogEntry:
    def __init__(self, line):
        self._token_map = {}

        for token in line.split():
            index = token.find("=");
            if index != -1:
                exploded = token.split('=', 1)
                key, value = exploded
                self._token_map[key] = value

                if key in _INTEGER_KEYS:
                    try:
                        setattr(self, key, int(value))
                    except ValueError:
                        pass
                elif key.isupper():
                    setattr(self, key, value)

        try:
            self.tcp_packet = self.PROTO == 'TCP'
        except AttributeError:
            self.tcp_packet = False

        try:
            self.extended_tcp_packet = self.tcp_packet and \
                self.DPT != None and \
                self.ID != None and \
                self.SEQ != None and \
                self.ACK != None and \
                self.WINDOW != None
        except AttributeError:
            self.extended_tcp_packet = False


    def get_destination_port(self):
        return int(self._token_map['DPT'])


    def get_source_ip(self):
        return self._token_map['SRC']


    def __repr__(self):
        mapping = sorted(self._token_map.items())
        value = ['%s=%s' % (k, v) for k, v in mapping]
        return '<LogEntry %s>' % ' '.join(value)

