#!/usr/bin/env python
import argparse
import os
import subprocess
import sys

from knockknock.profiles import Profiles
from knockknock.cli.log_setup import setup_logging


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='~/.knockknock',
                        help='Defaults to ~/.knockknock')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('host', help='Address of the knockknock server')

    args = parser.parse_args()
    args.config_dir = os.path.expanduser(args.config_dir)

    return args


def _get_profile(host, port, config_dir):
    profiles = Profiles(config_dir)
    return profiles.profile_for_hostport(host, port)


def _verify_permissions():
    if os.getuid() != 0:
        print 'Sorry, you must be root to run this.'
        sys.exit(2)


def _exists_in_path(command):
    def is_executable(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, command)
        if is_executable(exe_file):
            return exe_file


def _send_packet(hping, host, port, ID, SEQ, ACK, WIN):
    command = [hping, "-q",
               "-S", "-c", "1",
               "-p", '%d' % port,
               "-N", '%d' % ID,
               "-w", '%d' % WIN,
               "-M", '%d' % SEQ,
               "-L", '%d' % ACK,
               host]

    try:
        subprocess.call(command,
                        shell=False,
                        stdout=open('/dev/null', 'w'))
        print 'Knock sent.'

    except OSError:
        print "Error: Do you have hping3 installed?"
        sys.exit(3)


def main():
    args = _parse_arguments()
    setup_logging(args.verbose)
    _verify_permissions()

    hping = _exists_in_path("hping3")
    if not hping:
        print "Error, you must install hping3 first."
        sys.exit(2)

    profile = _get_profile(args.host, args.port, args.config_dir)
    packets = profile.generate()

    for port, ID, SEQ, ACK, WIN in packets:
        _send_packet(hping, args.host, args.port, ID, SEQ, ACK, WIN)


if __name__ == '__main__':
    main()

