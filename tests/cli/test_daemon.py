import flexmock
from knockknock.cli import daemon
from knockknock.knock_watcher import KnockWatcher


def test_daemon(config_dir):
    args = flexmock(config_dir=config_dir.strpath,
                    foreground=True,
                    verbose=True)

    d = flexmock(daemon)
    d.should_receive('_parse_arguments').and_return(args)
    d.should_receive('_check_privileges')

    k = flexmock(KnockWatcher)
    k.should_receive('tail_and_process')

    d.main()

