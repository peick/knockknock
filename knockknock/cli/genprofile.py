#!/usr/bin/env python
import argparse
import os
import sys

from knockknock.cli.log_setup import setup_logging
from knockknock.methods import METHODS, COUNTER
from knockknock.methods.counter import CounterConfig
from knockknock.profile_config import ProfileConfig
from knockknock.profiles import Profiles


DAEMON_DIR = '/etc/knockknock'


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', metavar='PROFILE_NAME')
    parser.add_argument('port', metavar='KNOCK_PORT', type=int)
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='/etc/knocknock.d')
    parser.add_argument('-m', metavar='METHOD',
                        dest='method')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    assert args.method in METHODS
    args.config_dir = os.path.expanduser(args.config_dir)

    return args


def _check_profile(profile_path):
    if os.path.exists(profile_path):
        print "Profile already exists: %s" % (profile_path, )
        sys.exit(1)


def _check_port_confflict(config_dir, host, port):
    profiles = Profiles(config_dir)
    match    = profiles.profile_for_hostport(host, port)

    if match:
        print "A profile already exists for host %s and port %d at %s" % (host, port, match.path)
        sys.exit(1)


def _create_directory(config_dir):
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)


def _generate_profile(method, host, port, profile_path):
    if method == COUNTER:
        random     = open('/dev/urandom', 'rb')
        cipher_key = random.read(16)
        mac_key    = random.read(16)
        counter    = 0
        window     = 16
        random.close()

        config = ProfileConfig(profile_path)
        config.host = host
        config.port = port
        config.method = COUNTER
        config.method_config = CounterConfig(cipher_key, mac_key, counter, window)
        config.store_config()

        print "Keys successfully generated in %s" % (profile_path, )
    else:
        raise Exception('unknown method: %r' % method)


def main():
    args = _parse_arguments()
    setup_logging(args.verbose)

    profile_path = os.path.join(args.config_dir, '%s-%s.conf' % (args.host, args.port))

    _check_profile(profile_path)
    _check_port_confflict(args.config_dir, args.host, args.port)
    _create_directory(args.config_dir)

    _generate_profile(args.method, args.host, args.port, profile_path)


if __name__ == '__main__':
    main()

