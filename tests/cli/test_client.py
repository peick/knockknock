import flexmock

from knockknock.profile_config import ProfileConfig
from knockknock.cli import client


def test_client(config_dir):
    # suppress saving of new counter value
    flexmock(ProfileConfig).should_receive('store_config')

    c = flexmock(client)
    c.should_receive('_parse_arguments') \
        .and_return((22, 'example.com', config_dir.strpath))
    c.should_receive('_verify_permissions')

    c.main()
