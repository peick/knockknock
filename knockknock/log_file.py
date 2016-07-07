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
import time


class LogFile:
    def __init__(self, path):
        self._path = path


    def _check_for_file_rotate(self, fd):
        fresh_file = open(self._path)

        if os.path.sameopenfile(fresh_file.fileno(), fd.fileno()):
            fresh_file.close()
            return fd
        else:
            fd.close()
            return fresh_file


    def tail(self):
        fd = open(self._path)
        fd.seek(0, os.SEEK_END)

        while True:
            fd    = self._check_for_file_rotate(fd)
            where = fd.tell()
            line  = fd.readline()

            if not line:
                time.sleep(0.25)
                fd.seek(where)
            else:
                yield line
