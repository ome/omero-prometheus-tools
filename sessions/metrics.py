#!/usr/bin/env python

import argparse
import collections
import omero.clients
import omero.cmd
from prometheus_client import (
    Gauge,
    Summary,
    start_http_server,
)
from time import sleep


def connect(hostname, username, password):
    client = omero.client(hostname)
    client.setAgent('prometheus-omero-py')
    client.createSession(username, password)
    return client


SESSION_REQUEST_TIME = Summary(
    'omero_sessions_processing_seconds', 'Time spent counting sessions')


class SessionMetrics(object):

    lastusers = set()
    g_sessions = Gauge(
        'omero_sessions_active', 'Active OMERO sessions', ['username'])
    g_last_login = Gauge('omero_sessions_agent_login_time',
                         'Time of last Prometheus agent login')
    g_login = Gauge('omero_sessions_agent_login',
                    'Prometheus agent logged in to OMERO')
    login_succeeded = False

    def __init__(self, hostname, username, password, verbose=False):
        self.connect_args = dict(
            hostname=hostname, username=username, password=password)
        self.verbose = verbose

    @SESSION_REQUEST_TIME.time()
    def update(self):
        # https://github.com/openmicroscopy/openmicroscopy/blob/v5.4.0-m1/components/tools/OmeroPy/src/omero/plugins/sessions.py#L714
        try:
            client = connect(**self.connect_args)
            self.g_login.set(1)
            self.g_last_login.set_to_current_time()
            if not self.login_succeeded or self.verbose:
                print('Login succeeded')
            self.login_succeeded = True
        except Exception as e:
            self.g_login.set(0)
            print('Login failed: %s' % e)
            self.login_succeeded = False
            return

        try:
            cb = client.submit(omero.cmd.CurrentSessionsRequest())
            try:
                rsp = cb.getResponse()
                counts = collections.Counter(c.userName for c in rsp.contexts)
                missing = self.lastusers.difference(counts.keys())
                for m in missing:
                    if self.verbose:
                        print('%s: %d' % (m, 0))
                    self.g_sessions.remove(m)
                    self.lastusers.remove(m)
                for username, n in counts.iteritems():
                    if self.verbose:
                        print('%s: %d' % (username, n))
                    self.g_sessions.labels(username).set(n)
                    self.lastusers.add(username)
            finally:
                cb.close(True)
        finally:
            client.closeSession()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-u', '--user', default='guest')
    parser.add_argument('-w', '--password', default='guest')
    parser.add_argument('-l', '--listen', type=int, required=True,
                        help='Serve metrics on this port (required)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    args = parser.parse_args()
    # Start up the server to expose the metrics.
    start_http_server(args.listen)
    metrics = SessionMetrics(
        args.host, args.user, args.password, verbose=args.verbose)
    while True:
        metrics.update()
        sleep(15)
