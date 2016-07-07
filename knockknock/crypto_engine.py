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

import hmac
import hashlib
import struct

from Crypto.Cipher import AES

from mac_failed_exception import MacFailedException


class CryptoEngine:
    def __init__(self, profile, cipher_key, mac_key, counter):
        self._profile    = profile
        self._counter    = counter
        self._mac_key    = mac_key
        self._cipher_key = cipher_key
        self._cipher     = AES.new(cipher_key, AES.MODE_ECB)


    def _calculate_mac(self, port):
        hmac_sha = hmac.new(self._mac_key, port, hashlib.sha1)
        mac      = hmac_sha.digest()
        return mac[:10]


    def _verify_mac(self, port, remote_mac):
        local_mac = self._calculate_mac(port)

        if (local_mac != remote_mac):
            raise MacFailedException, "MAC Doesn't Match!"


    def _encrypt_counter(self, counter):
        counter_bytes = struct.pack('!IIII', 0, 0, 0, counter)
        return self._cipher.encrypt(counter_bytes)


    def encrypt(self, plaintext_data):
        plaintext_data += self._calculate_mac(plaintext_data)
        counter_crypt   = self._encrypt_counter(self._counter)
        self._counter  += 1
        encrypted       = ''

        for i in range((len(plaintext_data))):
            encrypted += chr(ord(plaintext_data[i]) ^ ord(counter_crypt[i]))

        self._profile.counter = self._counter
        self._profile.store_counter()

        return encrypted


    def decrypt(self, encrypted_data, window_size):
        for x in range(window_size):
            try:
                counter_crypt = self._encrypt_counter(self._counter + x)
                decrypted     = ''

                for i in range((len(encrypted_data))):
                    decrypted += chr(ord(encrypted_data[i]) ^ ord(counter_crypt[i]))

                port = decrypted[:2]
                mac  = decrypted[2:]

                self._verify_mac(port, mac)
                self._counter += x + 1

                self._profile.counter = self._counter
                self._profile.store_counter()

                return int(struct.unpack("!H", port)[0])

            except MacFailedException:
                pass

        raise MacFailedException, "Ciphertext failed to decrypt in range..."

