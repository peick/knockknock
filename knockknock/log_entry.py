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


class LogEntry:
    def __init__(self, line):
        self._build_token_map(line)


    def _build_token_map(self, line):
        self._token_map = dict()

        for token in line.split():
            index = token.find("=");
            if index != -1:
                exploded = token.split('=')
                self._token_map[exploded[0]] = exploded[1]


    def is_valid_tcp_packet(self):
        return (self._token_map.get('DPT')
                and self._token_map.get('SPT')
                and self._token_map.get('SEQ'))


    def get_destination_port(self):
        return int(self._token_map['DPT'])


    def get_encrypted_data(self):
        return struct.pack('!HIIH',
                           int(self._token_map['ID']),
                           int(self._token_map['SEQ']),
                           int(self._token_map['ACK']),
                           int(self._token_map['WINDOW']))


    def get_source_ip(self):
        return self._token_map['SRC']


    def __repr__(self):
        mapping = sorted(self._token_map.items())
        value = ['%s=%s' % (k, v) for k, v in mapping]
        return '<LogEntry %s>' % ' '.join(value)
