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
import subprocess
import syslog

from rule_timer import RuleTimer


class PortOpener:
    IPTABLES_RULE = ('%s -m limit'
                     ' --limit 1/minute'
                     ' --limit-burst 1'
                     ' -m state'
                     ' --state NEW'
                     ' -p tcp'
                     ' -s %s'
                     ' --dport %d'
                     ' -j ACCEPT')


    def __init__(self, stream):
        self._stream = stream


    def wait_for_requests(self):
        while True:
            source_ip     = self._stream.readline().rstrip("\n")
            port          = self._stream.readline().rstrip("\n")
            open_duration = self._stream.readline().rstrip("\n")
            table         = self._stream.readline().rstrip("\n")

            if not source_ip or not port or not open_duration or not table:
                syslog.syslog("knockknock.PortOpener: Parent process is closed. Terminating.")
                os._exit(4)

            port          = int(port)
            open_duration = int(open_duration)
            description   = self.IPTABLES_RULE % (table, source_ip, port)
            command       = 'iptables -I ' + description
            command       = command.split()

            print "Opening port %d for %s" % (port, source_ip)
            subprocess.call(command, shell=False)

            RuleTimer(open_duration, description).start()


    def open(self, source_ip, port, open_duration, table):
        try:
            self._stream.write("%s\n" % source_ip)
            self._stream.write("%d\n" % port)
            self._stream.write("%d\n" % open_duration)
            self._stream.write("%s\n" % table)
            self._stream.flush()
        except:
            syslog.syslog("knockknock:  Error, PortOpener process has died.  Terminating.")
            os._exit(4)

