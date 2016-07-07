import flexmock
from knockknock.cli import client


def test_client(config_dir):
    c = flexmock(client)
    c.should_receive('_parse_arguments') \
        .and_return((999, 'localhost', config_dir.strpath))
    c.should_receive('_verify_permissions')

    c.main()
