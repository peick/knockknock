import flexmock
from knockknock.cli import daemon
from knockknock.knock_watcher import KnockWatcher


def test_daemon(config_dir):
    d = flexmock(daemon)
    d.should_receive('_parse_arguments') \
        .and_return((config_dir.strpath, True))
    d.should_receive('_check_privileges')

    k = flexmock(KnockWatcher)
    k.should_receive('tail_and_process')

    d.main()

