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


def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('host', help='Address of the knockknock server')

    args = parser.parse_args()

    return (args.port, args.host)

def getProfile(host):
    homedir = os.path.expanduser('~')

    if not os.path.isdir(homedir + '/.knockknock/'):
        print "Error: you need to setup your profiles in " + homedir + '/.knockknock/'
        sys.exit(2)

    if not os.path.isdir(homedir + '/.knockknock/' + host):
        print 'Error: profile for host ' + host + ' not found at ' + homedir + '/.knockknock/' + host
        sys.exit(2)

    return Profile(homedir + '/.knockknock/' + host)

def verifyPermissions():
    if os.getuid() != 0:
        print 'Sorry, you must be root to run this.'
        sys.exit(2)

def existsInPath(command):
    def isExe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exeFile = os.path.join(path, command)
        if isExe(exeFile):
            return exeFile

    return None

def main():
    (port, host) = parseArguments()
    verifyPermissions()

    profile      = getProfile(host)
    port         = struct.pack('!H', int(port))
    packetData   = profile.encrypt(port)
    knockPort    = profile.getKnockPort()

    (idField, seqField, ackField, winField) = struct.unpack('!HIIH', packetData)

    hping = existsInPath("hping3")

    if hping is None:
        print "Error, you must install hping3 first."
        sys.exit(2)

    command = [hping, "-S", "-c", "1",
               "-p", str(knockPort),
               "-N", str(idField),
               "-w", str(winField),
               "-M", str(seqField),
               "-L", str(ackField),
               host]

    try:
        subprocess.call(command, shell=False, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
        print 'Knock sent.'

    except OSError:
        print "Error: Do you have hping3 installed?"
        sys.exit(3)

if __name__ == '__main__':
    main()
