from knockknock.methods import counter, timer


COUNTER = 'counter'
TIMER   = 'timer'


METHODS = [COUNTER, TIMER]


def config_by_name(name, parser):
    if name == COUNTER:
        return counter.CounterConfig.from_config_parser(parser)

    if name == TIMER:
        return timer.TimerConfig.from_config_parser(parser)

    raise KeyError(name)


def profile_by_name(name, config):
    if name == COUNTER:
        return counter.CounterProfile(config)

    if name == TIMER:
        return timer.TimerProfile(config)

    raise KeyError(name)
