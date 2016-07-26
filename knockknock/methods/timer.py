"""Time based verification. Requires that the clocks of server and client are
synchronized.
"""
import time

from knockknock.methods.counter import BaseCounterConfig, BaseCounterProfile
from knockknock.profile_config import int_


class TimerConfig(BaseCounterConfig):
    def __init__(self, cipher_key, mac_key, window, resolution):
        BaseCounterConfig.__init__(self, cipher_key, mac_key, window)
        if resolution is None:
            raise ValueError('invalid resolution')

        self.resolution = int_(resolution, min_value=1)


    @staticmethod
    def from_config_parser(parser):
        cipher_key, mac_key, window = \
            BaseCounterConfig.from_config_parser(parser, 'timer')

        resolution = parser.get('timer', 'resolution')
        return TimerConfig(cipher_key, mac_key, window, resolution)


    def store_config(self, parser):
        BaseCounterConfig.store_config(parser, 'timer')
        parser.set('timer', 'resolution', '%d' % self.resolution)


class TimerProfile(BaseCounterProfile):
    def _update_config(self, new_counter):
        pass


    def _current_counter(self):
        config = self._config.method_config
        now    = int(time.time())
        return (now / config.resolution) - (config.window / 2)

