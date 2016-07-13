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


class KnockWatcher:
    def __init__(self, log_file, profiles, port_opener):
        self._log_file    = log_file
        self._profiles    = profiles
        self._port_opener = port_opener


    def tail_and_process(self):
        for line in self._log_file.tail():
            try:
                log_entry = LogEntry(line)

                for profile in self._profiles.filter(log_entry):
                    print "got knock attempt: %r" % log_entry
                    iptables_table, open_duration, port = profile.verify(log_entry)

                    if not port:
                        continue

                    source_ip = log_entry.get_source_ip()

                    self._port_opener.open(source_ip, port, open_duration, iptables_table)
                    syslog.syslog("Received authenticated port-knock for port " + str(port) + " from " + source_ip)
            except:
                syslog.syslog("knocknock skipping unrecognized line: %s" % line[:120])

