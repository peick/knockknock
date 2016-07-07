import flexmock
import pytest
from knockknock.cli import client


def test_client(config_dir):
    c = flexmock(client)
    c.should_receive('_parse_arguments') \
        .and_return((999, 'localhost', config_dir.strpath))
    c.should_receive('_verify_permissions')

    # knock sending failed because tests are not executed as root
    with pytest.raises(SystemExit) as error:
        c.main()

    assert error.value.code == 4
