import flexmock

from knockknock.profile_config import ProfileConfig
from knockknock.cli import client


def test_client(config_dir):
    # suppress saving of new counter value
    flexmock(ProfileConfig).should_receive('store_config')

    args = flexmock(port=22,
                    host='example.com',
                    config_dir=config_dir.strpath,
                    verbose=True)

    c = flexmock(client)
    c.should_receive('_parse_arguments').and_return(args)
    c.should_receive('_verify_permissions')

    c.main()
