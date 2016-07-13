import ConfigParser

import flexmock

from knockknock.cli import genprofile


def test_client(tmpdir):
    c = flexmock(genprofile)
    c.should_receive('_parse_arguments') \
        .and_return(('counter', 'localhost', 999, tmpdir.strpath))

    c.main()

    dest = tmpdir.join('localhost-999.conf')
    assert dest.exists()

    parser = ConfigParser.SafeConfigParser()
    parser.readfp(open(dest.strpath))

    assert parser.get('knockknock', 'host') == 'localhost'
    assert parser.get('knockknock', 'port') == '999'
    assert parser.get('knockknock', 'method') == 'counter'
    assert parser.get('counter', 'cipher_key')
    assert parser.get('counter', 'mac_key')
    assert parser.get('counter', 'counter') == '0'
    assert parser.get('counter', 'window') == '16'

