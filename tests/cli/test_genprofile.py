import flexmock
from knockknock.cli import genprofile


def test_client(tmpdir):
    c = flexmock(genprofile)
    c.should_receive('_parse_arguments') \
        .and_return((999, 'localhost', tmpdir.strpath))

    c.main()

    destdir = tmpdir.join('profiles').join('localhost')
    assert destdir.join('cipher.key').read()
    assert destdir.join('mac.key').read()
    assert destdir.join('counter').read().strip() == '0'
    assert destdir.join('config').read().replace(' ', '').strip() == '[main]\nknock_port=999'
