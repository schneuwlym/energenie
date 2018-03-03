#!/usr/bin/env python
"""
:Author: Mathias Schneuwly

This module provides a simple interface to control an Energenie power socket.
"""

import argparse
import re
import urllib
import urllib2
import fcntl
import sys
import signal
import errno
import os
from contextlib import contextmanager


@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        pass

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)

    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


class Energenie(object):

    def __init__(self, ip, password, timeout=5):
        self._ip = ip
        self._password = password
        self._timeout = timeout

    def _do_request(self, url, data=None):
        if data is not None:
            data = urllib.urlencode(data)
        req = urllib2.Request(url=url,
                              data=data)
        f = urllib2.urlopen(req, timeout=self._timeout)
        result = f.read()
        f.close()
        return result

    def login(self):
        res = self._do_request(url='http://%s/login.html' % self._ip,
                               data={'pw': self._password})
        if res == '' or 'EnerGenie Web:' in res:
            return False
        return True

    def logout(self):
        res = self._do_request(url='http://%s/login.html' % self._ip,
                               data={'pw': ''})
        if 'EnerGenie Web:' in res:
            return True
        return False

    def get_socket_state(self, socket=None):
        if socket is not None and socket not in xrange(1, 5):
            raise Exception('Socket must be None or an integer between 1 and 4')
        result = {}

        tmp = self._do_request(url='http://%s/energenie.html' % self._ip)

        try:
            found = re.search('var sockstates = \[(.*)\];', tmp).group(1)
        except AttributeError as err:
            raise Exception('Socket state not found: %s (%s)' % (str(err), str(tmp)))
        socket_state = found.split(',')
        for s, state in enumerate(socket_state):
            result[s+1] = bool(int(state))
        if socket is None:
            return result
        else:
            return result[socket]

    def set_socket_state(self, socket, state):
        if socket is None:
            for i in xrange(1, 5):
                data = {'cte%d' % i: int(state)}
                self._do_request(url='http://%s' % self._ip,
                                 data=data)
        else:
            data = {'cte%d' % socket: int(state)}
            self._do_request(url='http://%s' % self._ip,
                             data=data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control Energenie sockets')
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('--ip', '-i', type=str, dest='ip', required=True,
                        help='')
    parser.add_argument('--password', '-p', type=str, dest='password', required=True,
                        help='')
    parser.add_argument('--socket', '-s', type=int, dest='socket', choices=range(1, 5), default=None,
                        help='')
    parser.add_argument('--timeout', '-t', type=int, dest='timeout', default=5,
                        help='')
    parser.add_argument('--pid', type=str, dest='pidfile', default='/var/run/energenie.pid',
                        help='')
    group.add_argument('--enable', '-e', dest='state', action='store_true',
                        help='')
    group.add_argument('--disable', '-d', dest='state', action='store_false',
                        help='')
    group.add_argument('--get_state', '-g', dest='get', action='store_true', default=False,
                       help='')

    args = parser.parse_args()

    try:
        fp = open(args.pidfile, 'w')
        with timeout(5):
            try:
                #fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.lockf(fp, fcntl.LOCK_EX)
            except IOError:
                sys.exit(1)

        energenie = Energenie(args.ip, args.password, args.timeout)
        try:
            if not energenie.login():
                raise Exception('Could not login')
            if args.get:
                print energenie.get_socket_state(args.socket)
            else:
                energenie.set_socket_state(args.socket, args.state)
        finally:
            if not energenie.logout():
                raise Exception('Could not logout')
    finally:
        fp.close()
        if os.path.exists(args.pidfile):
            os.remove(args.pidfile)

