import os
import six
import stat
import ConfigParser


def non_empty_string(value):
    if not isinstance(value, six.string_types):
        raise ValueError('invalid type: %s' % value.__class__)

    if not value:
        raise ValueError('invalid value')

    return value


def int_(value, min_value=None, max_value=None):
    value = int(value)
    if min_value is not None and value < min_value:
        raise ValueError('invalid min value')

    if max_value is not None and value > max_value:
        raise ValueError('invalid max value')

    return value


class ProfileConfig:
    def __init__(self, config_file):
        self._port           = None
        self._host           = None
        self._method         = None
        self._method_config  = None
        self._open_duration  = 15
        self._config_file    = config_file
        self._iptables_table = 'INPUT'

        if os.path.exists(config_file):
            self._load_config()


    @property
    def path(self):
        return self._config_file


    @property
    def iptables_table(self):
        return self._iptables_table


    @property
    def port(self):
        return self._port


    @property
    def host(self):
        return self._host


    @property
    def open_duration(self):
        return self._open_duration


    @property
    def method(self):
        return self._method


    @property
    def method_config(self):
        return self._method_config


    @iptables_table.setter
    def iptables_table(self, value):
        self._iptables_table = non_empty_string(value)


    @port.setter
    def port(self, value):
        self._port = int_(value, 1, 65535)


    @host.setter
    def host(self, value):
        self._host = non_empty_string(value)


    @open_duration.setter
    def open_duration(self, value):
        self._open_duration = int_(value, 1)


    @method.setter
    def method(self, value):
        from knockknock.methods import METHODS

        if value not in METHODS:
            raise ValueError('invalid method')

        self._method = value


    @method_config.setter
    def method_config(self, value):
        self._method_config = value


    def _load_config(self):
        from knockknock.methods import config_by_name

        f = open(self._config_file)
        parser = ConfigParser.SafeConfigParser()
        parser.readfp(f)

        self.port           = parser.getint('knockknock', 'port')
        self.host           = parser.get('knockknock', 'host')
        self.method         = parser.get('knockknock', 'method')
        self.iptables_table = parser.get('knockknock', 'iptables-table')

        self.method_config = config_by_name(self.method, parser)


    def store_config(self):
        if not self.port or not self.host or not self.method or not self.method_config:
            raise ValueError('missing fields')

        parser = ConfigParser.SafeConfigParser()
        parser.add_section('knockknock')
        parser.set('knockknock', 'port', '%d' % self.port)
        parser.set('knockknock', 'host', self.host)
        parser.set('knockknock', 'method', self.method)
        parser.set('knockknock', 'iptables-table', self.iptables_table)

        self.method_config.store_config(parser)

        f = open(self._config_file, 'w')
        parser.write(f)

        self._set_permissions(self._config_file)


    def _set_permissions(self, path):
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

