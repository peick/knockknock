import pytest

from knockknock.log_entry import LogEntry
from knockknock.profile_config import ProfileConfig
from knockknock.methods.counter import CounterProfile, CryptoEngine


_ENCRYPTED   = "\xca_\x16\xe3N0w\xd6w\x8d\xabS"
_PORT        = 29541
_PORT_STRING = 'se'

# generated with counter 42 for port 22
_ENC_ID  = 0xb92c
_ENC_SEQ = 0x37efc8b4
_ENC_ACK = 0xfd562606
_ENC_WIN = 0xbbd3


@pytest.fixture
def profile(config_dir, tmpdir):
    path = config_dir.join('example.com-22.conf')
    dest = tmpdir.join(path.basename)
    path.copy(dest)

    config = ProfileConfig(dest.strpath)
    return CounterProfile(config)


@pytest.fixture
def engine():
    return CryptoEngine('akee' * 8, 'mackie')


def test_engine_encrypt(engine):
    result = engine.encrypt(42, _PORT_STRING)
    assert result == (43, _ENCRYPTED)


def test_engine_decrypt(engine):
    result = engine.decrypt(42, _ENCRYPTED, 16)
    assert result == (43, _PORT)


def test_engine_window(engine):
    encrypted = set()
    for idx in range(16):
        encrypted.add(engine.encrypt(42 + idx, _PORT_STRING))

    # verify uniqueness
    assert len(encrypted) == 16

    for counter, value in encrypted:
        result = engine.decrypt(42, value, 16)
        assert 42 < counter <= 42 + 16
        assert result == (counter, _PORT)


def test_profile_generate(profile):
    packets = profile.generate()

    assert len(packets) == 1
    port, ID, SEQ, ACK, WIN = packets[0]

    assert port == 22
    assert ID   == _ENC_ID
    assert SEQ  == _ENC_SEQ
    assert ACK  == _ENC_ACK
    assert WIN  == _ENC_WIN


def test_profile_verify(profile):
    log_entry = LogEntry('ID=%s SEQ=%s ACK=%s WINDOW=%s' % (
        _ENC_ID, _ENC_SEQ, _ENC_ACK, _ENC_WIN))

    table, open_duration, port = profile.verify(log_entry)

    assert table == 'ufw-after-input'
    assert open_duration == 15
    assert port == 22
    assert profile._config.method_config.counter == 43


@pytest.mark.parametrize('line, expect', [
    ('', False),
    ('PROTO=TCP', False),
    ('PROTO=TCP DPT=22 ID=1 SEQ=2 ACK=3 WINDOW=4', True),
    ('PROTO=TCP DPT=22 ID=0 SEQ=0 ACK=0 WINDOW=0', True),
])
def test_profile_match(profile, line, expect):
    log_entry = LogEntry(line)

    match = profile.match(log_entry)

    assert match == expect, log_entry

