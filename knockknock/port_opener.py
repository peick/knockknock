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
    IPTABLES_RULE = ('INPUT -m limit'
                     ' --limit 1/minute'
                     ' --limit-burst 1'
                     ' -m state'
                     ' --state NEW'
                     ' -p tcp'
                     ' -s %s'
                     ' --dport %d'
                     ' -j ACCEPT')


    def __init__(self, stream, open_duration):
        self._stream        = stream
        self._open_duration = open_duration


    def wait_for_requests(self):
        while True:
            source_ip = self._stream.readline().rstrip("\n")
            port      = self._stream.readline().rstrip("\n")

            if not source_ip or not port:
                syslog.syslog("knockknock.PortOpener: Parent process is closed.  Terminating.")
                os._exit(4)

            port        = int(port)
            description = self.IPTABLES_RULE % (source_ip, port)
            command     = 'iptables -I ' + description
            command     = command.split()

            print "Opening port %d for %s" % (port, source_ip)
            subprocess.call(command, shell=False)

            RuleTimer(self._open_duration, description).start()


    def open(self, source_ip, port):
        try:
            self._stream.write(source_ip + "\n")
            self._stream.write(str(port) + "\n")
            self._stream.flush()
        except:
            syslog.syslog("knockknock:  Error, PortOpener process has died.  Terminating.")
            os._exit(4)

