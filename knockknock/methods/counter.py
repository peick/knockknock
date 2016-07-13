import hmac
import hashlib
import struct

from Crypto.Cipher import AES

from knockknock.methods.mac_failed_exception import MacFailedException
from knockknock.methods.base import Profile
from knockknock.profile_config import int_


class CounterConfig:
    def __init__(self, cipher_key, mac_key, counter, window):
        if not cipher_key:
            raise ValueError('invalid cipher_key')
        if not mac_key:
            raise ValueError('invalid mac_key')
        if counter is None:
            raise ValueError('invalid counter')
        if not window:
            raise ValueError('invalid window')

        self.cipher_key = cipher_key
        self.mac_key    = mac_key
        self.counter    = int_(counter, min_value=0)
        self.window     = int_(window,  min_value=1)


    @staticmethod
    def from_config_parser(parser):
        deserialize = lambda b: b.decode('base64')
        cipher_key  = deserialize(parser.get('counter', 'cipher_key'))
        mac_key     = deserialize(parser.get('counter', 'mac_key'))
        counter     = parser.get('counter', 'counter')
        window      = parser.get('counter', 'window')
        return CounterConfig(cipher_key, mac_key, counter, window)


    def store_config(self, parser):
        parser.add_section('counter')
        serialize = lambda b: b.encode('base64').replace('\n', '')
        parser.set('counter', 'cipher_key', serialize(self.cipher_key))
        parser.set('counter', 'mac_key',    serialize(self.mac_key))
        parser.set('counter', 'window',     '%d' % self.window)
        parser.set('counter', 'counter',    '%d' % self.counter)


class CryptoEngine:
    def __init__(self, cipher_key, mac_key):
        self._mac_key    = mac_key
        self._cipher_key = cipher_key
        self._cipher     = AES.new(cipher_key, AES.MODE_ECB)


    def _calculate_mac(self, port):
        hmac_sha = hmac.new(self._mac_key, port, hashlib.sha1)
        mac      = hmac_sha.digest()
        return mac[:10]


    def _verify_mac(self, port, remote_mac):
        local_mac = self._calculate_mac(port)

        if local_mac != remote_mac:
            raise MacFailedException, "MAC Doesn't Match!"


    def _encrypt_counter(self, counter):
        counter_bytes = struct.pack('!IIII', 0, 0, 0, counter)
        return self._cipher.encrypt(counter_bytes)


    def encrypt(self, counter, plaintext_data):
        plaintext_data += self._calculate_mac(plaintext_data)
        counter_crypt   = self._encrypt_counter(counter)
        encrypted       = ''

        for i in range((len(plaintext_data))):
            encrypted += chr(ord(plaintext_data[i]) ^ ord(counter_crypt[i]))

        return counter + 1, encrypted


    def decrypt(self, start_counter, encrypted_data, window_size):
        for counter in range(start_counter, start_counter + window_size + 1):
            try:
                counter_crypt = self._encrypt_counter(counter)
                decrypted     = ''

                for i in range((len(encrypted_data))):
                    decrypted += chr(ord(encrypted_data[i]) ^ ord(counter_crypt[i]))

                port = decrypted[:2]
                mac  = decrypted[2:]

                self._verify_mac(port, mac)

                return counter + 1, int(struct.unpack("!H", port)[0])

            except MacFailedException:
                pass

        raise MacFailedException, "Ciphertext failed to decrypt in range..."


class CounterProfile(Profile):
    def __init__(self, config):
        Profile.__init__(self, config)


    def match(self, log_entry):
        return log_entry.extended_tcp_packet


    def verify(self, log_entry):
        settings = self._config.method_config

        crypto_engine = CryptoEngine(settings.cipher_key,
                                     settings.mac_key)

        ciphered = struct.pack('!HIIH',
                               log_entry.ID,
                               log_entry.SEQ,
                               log_entry.ACK,
                               log_entry.WINDOW)

        try:
            new_counter, port = crypto_engine.decrypt(settings.counter,
                                                      ciphered,
                                                      settings.window)

            self._config.method_config.counter = new_counter
            self._config.store_config()

            return self._config.iptables_table, self._config.open_duration, port
        except MacFailedException:
            return


    def generate(self):
        settings = self._config.method_config

        crypto_engine = CryptoEngine(settings.cipher_key,
                                     settings.mac_key)

        plaintext = struct.pack('!H', self._config.port)

        new_counter, ciphered = crypto_engine.encrypt(settings.counter,
                                                      plaintext)

        self._config.method_config.counter = new_counter
        self._config.store_config()

        ID, SEQ, ACK, WIN = struct.unpack('!HIIH', ciphered)
        return [(self._config.port, ID, SEQ, ACK, WIN)]

