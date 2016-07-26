#!/usr/bin/env python
import argparse
import asyncore
import os
import socket
import sys

import knockknock.daemonize
from knockknock.cli.log_setup import setup_logging
from knockknock.profiles import Profiles
from knockknock.proxy.socks_request_handler import SocksRequestHandler


class ProxyServer(asyncore.dispatcher):
    def __init__(self, port, profiles):
        asyncore.dispatcher.__init__(self)
        self.profiles = profiles
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("127.0.0.1", port))
        self.listen(5)


    def handle_accept(self):
        conn, _addr = self.accept()
        SocksRequestHandler(conn, self.profiles)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-dir',
                        dest='config_dir',
                        default='~/.knockknock')
    parser.add_argument('port', metavar='LISTEN_PORT', type=int)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    args.config_dir = os.path.expanduser(args.config_dir)

    return args.port, args.config_dir


def _get_profiles(config_dir):
    profiles_dir = os.path.join(config_dir)
    profiles     = Profiles(profiles_dir)

    profiles.resolve_names()

    return profiles


def _check_privileges():
    if not os.geteuid() == 0:
        print "\nSorry, knockknock-proxy has to be run as root.\n"
        sys.exit(2)


def _check_profiles(config_dir):
    if not os.path.isdir(config_dir):
        print "Error: you need to setup your profiles in %s" % (config_dir, )
        sys.exit(2)


def main():
    raise Exception('got broken by refactoring')
    args = _parse_arguments()
    setup_logging(args.verbose)

    _check_privileges()
    _check_profiles(args.config_dir)

    profiles = _get_profiles(args.config_dir)
    ProxyServer(args.port, profiles)

    knockknock.daemonize.createDaemon()

    asyncore.loop(use_poll=True)


if __name__ == '__main__':
    main()

