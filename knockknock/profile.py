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

import binascii
import os
import stat
import ConfigParser

from crypto_engine import CryptoEngine


class Profile:
    def __init__(self, directory, cipher_key=None, mac_key=None, counter=None, knock_port=None):
        self._counter_file = None
        self._directory    = directory.rstrip('/')
        self.name          = os.path.basename(self._directory)

        if cipher_key is None:
            self._deserialize()
        else:
            self._cipher_key = cipher_key
            self._mac_key    = mac_key
            self._counter    = counter
            self.knock_port  = knock_port

        self._crypto_engine = CryptoEngine(self, self._cipher_key, self._mac_key, self._counter)

        self.ip_addrs       = []


    def _deserialize(self):
        self._cipher_key = self._load_cipher_key()
        self._mac_key    = self._load_mac_key()
        self._counter    = self._load_counter()
        self.knock_port  = self._load_config()


    def serialize(self):
        self._store_cipher_key()
        self._store_mac_key()
        self.store_counter()
        self._store_config()


    def decrypt(self, ciphertext, window_size):
        return self._crypto_engine.decrypt(ciphertext, window_size)


    def encrypt(self, plaintext):
        return self._crypto_engine.encrypt(plaintext)


    def _load_cipher_key(self):
        return self._load_key(os.path.join(self._directory, 'cipher.key'))


    def _load_mac_key(self):
        return self._load_key(os.path.join(self._directory, 'mac.key'))


    def _load_counter(self):
        # Privsep bullshit...
        if self._counter_file == None:
            self._counter_file = open(os.path.join(self._directory, 'counter'), 'r+')

        counter = self._counter_file.readline()
        counter = counter.rstrip("\n")

        return int(counter)


    def _load_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.join(self._directory, 'config'))

        return int(config.get('main', 'knock_port'))


    def _load_key(self, key_file):
        file = open(key_file)
        key  = binascii.a2b_base64(file.readline())

        file.close()
        return key


    def _store_cipher_key(self):
        self._store_key(self._cipher_key, os.path.join(self._directory, 'cipher.key'))


    def _store_mac_key(self):
        self._store_key(self._mac_key, os.path.join(self._directory, 'mac.key'))


    def store_counter(self):
        # Privsep bullshit...
        if self._counter_file == None:
            self._counter_file = open(os.path.join(self._directory, 'counter'), 'w')
            self._set_permissions(os.path.join(self._directory, 'counter'))

        self._counter_file.seek(0)
        self._counter_file.write(str(self._counter) + "\n")
        self._counter_file.flush()


    def _store_config(self):
        path = os.path.join(self._directory, 'config')

        config = ConfigParser.SafeConfigParser()
        config.add_section('main')
        config.set('main', 'knock_port', '%d' % self.knock_port)

        config_file = open(path, 'w')
        config.write(config_file)
        config_file.close()

        self._set_permissions(path)


    def _store_key(self, key, path):
        file = open(path, 'w')
        file.write(binascii.b2a_base64(key))
        file.close()

        self._set_permissions(path)

    # Permissions

    def _set_permissions(self, path):
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

