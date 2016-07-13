from knockknock.methods import counter


COUNTER = 'counter'


METHODS = [COUNTER]


def config_by_name(name, parser):
    if name == COUNTER:
        return counter.CounterConfig.from_config_parser(parser)

    raise KeyError(name)


def profile_by_name(name, config):
    if name == COUNTER:
        return counter.CounterProfile(config)

    raise KeyError(name)
