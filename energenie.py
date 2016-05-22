#!/usr/bin/env python
"""
:Author: Mathias Schneuwly

This module provides a simple interface to control an Energenie power socket.
"""

import argparse
import re
import urllib
import urllib2


class Energenie(object):

    def __init__(self, ip, password):
        self._ip = ip
        self._password = password

    def _do_request(self, url, data=None):
        if data is not None:
            data = urllib.urlencode(data)
        req = urllib2.Request(url=url,
                              data=data)

        f = urllib2.urlopen(req)
        result = f.read()
        f.close()
        return result

    def login(self):
        self._do_request(url='http://%s/login.html' % self._ip,
                         data={'pw': self._password})

    def logout(self):
        self._do_request(url='http://%s/login.html' % self._ip,
                         data={'pw': ''})

    def get_socket_state(self, socket=None):
        if socket is not None and socket not in xrange(1, 5):
            raise Exception('Socket must be None or an integer between 1 and 4')
        result = {}

        tmp = self._do_request(url='http://%s/energenie.html' % self._ip)

        try:
            found = re.search('var sockstates = \[(.*)\];', tmp).group(1)
        except AttributeError:
            raise Exception('Socket state not found')
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
    group.add_argument('--enable', '-e', dest='state', action='store_true',
                        help='')
    group.add_argument('--disable', '-d', dest='state', action='store_false',
                        help='')
    group.add_argument('--get_state', '-g', dest='get', action='store_true', default=False,
                       help='')

    args = parser.parse_args()

    energenie = Energenie(args.ip, args.password)
    energenie.login()
    if args.get:
        print energenie.get_socket_state(args.socket)
    else:
        energenie.set_socket_state(args.socket, args.state)
    energenie.logout()
