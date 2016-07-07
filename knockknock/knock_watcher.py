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

import syslog

from log_entry import LogEntry
from mac_failed_exception import MacFailedException


class KnockWatcher:
    def __init__(self, config, log_file, profiles, port_opener):
        self._config      = config
        self._log_file    = log_file
        self._profiles    = profiles
        self._port_opener = port_opener


    def tail_and_process(self):
        for line in self._log_file.tail():
            try:
                log_entry = LogEntry(line)

                if not log_entry.is_valid_tcp_packet():
                    continue

                port      = log_entry.get_destination_port()
                profile   = self._profiles.get_profile_for_port(port)

                if profile:
                    print "got knock attempt: %r" % log_entry
                    try:
                        ciphertext = log_entry.get_encrypted_data()
                        window     = self._config.window
                        port       = profile.decrypt(ciphertext, window)
                        source_ip  = log_entry.get_source_ip()

                        self._port_opener.open(source_ip, port)
                        syslog.syslog("Received authenticated port-knock for port " + str(port) + " from " + source_ip)
                    except MacFailedException:
                        pass
            except:
                syslog.syslog("knocknock skipping unrecognized line: %s" % line[:120])

