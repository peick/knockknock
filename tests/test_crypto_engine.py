import flexmock
import pytest

from knockknock.crypto_engine import CryptoEngine


_ENCRYPTED = "\xca_\x16\xe3N0w\xd6w\x8d\xabS"
_PORT             = 29541
_PORT_STRING      = 'se'


@pytest.fixture
def profile():
    return flexmock()


@pytest.fixture
def engine(profile):
    return CryptoEngine(profile, 'akee' * 8, 'mackie', 42)


def test_encrypt(profile, engine):
    profile.should_receive('store_counter').with_args(43).once()

    result = engine.encrypt(_PORT_STRING)
    assert result == _ENCRYPTED


def test_decrypt(profile, engine):
    profile.should_receive('store_counter').with_args(43).once()

    result = engine.decrypt(_ENCRYPTED, 16)
    assert result == _PORT


def test_window(profile, engine):
    profile.should_receive('set_counter')
    profile.should_receive('store_counter')

    encrypted = set()
    for idx in range(16):
        encrypted.add(engine.encrypt(_PORT_STRING))

    # verify uniqueness
    assert len(encrypted) == 16

    for value in encrypted:
        engine._counter = 42
        result = engine.decrypt(value, 16)
        assert result == _PORT

