import ConfigParser
from knockknock.profile_config import ProfileConfig
from knockknock.methods.counter import CounterConfig


def test_config_new(tmpdir):
    path = tmpdir.join('config_new.conf')
    config = ProfileConfig(path.strpath)

    assert config.port is None
    assert config.host is None
    assert config.method is None
    assert config.method_config is None


def test_store_new_config(tmpdir):
    path = tmpdir.join('store_new_config.conf')
    config = ProfileConfig(path.strpath)

    config.port = 22
    config.host = 'example.com'
    config.method = 'counter'
    config.method_config = CounterConfig('cipher-KEY', 'mac-KEY', 5, 16)
    config.store_config()

    # verify
    parser = ConfigParser.SafeConfigParser()
    parser.read([path.strpath])

    assert parser.getint('knockknock', 'port') == 22
    assert parser.get('knockknock', 'host') == 'example.com'
    assert parser.get('knockknock', 'method') == 'counter'
    assert parser.get('counter', 'cipher_key') == 'Y2lwaGVyLUtFWQ=='
    assert parser.get('counter', 'mac_key') == 'bWFjLUtFWQ=='
    assert parser.getint('counter', 'counter') == 5
    assert parser.getint('counter', 'window') == 16


def test_load_config(config_dir):
    path = config_dir.join('example.com-22-counter.conf')
    config = ProfileConfig(path.strpath)

    assert config.port == 22
    assert config.host == 'example.com'
    assert config.method == 'counter'
    assert config.method_config
    assert config.method_config.cipher_key == 'akee' * 8
    assert config.method_config.mac_key == 'mac-KEY'
    assert config.method_config.counter == 42
    assert config.method_config.window == 16

