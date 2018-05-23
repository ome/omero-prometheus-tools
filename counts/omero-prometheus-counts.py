#!/usr/bin/env python

import argparse
import omero.clients
import omero.cmd
import omero
from omero.rtypes import unwrap

from prometheus_client import (
    Gauge,
    Summary,
    start_http_server,
)
from time import sleep


def connect(hostname, username, password):
    client = omero.client(hostname)
    client.setAgent('prometheus-omero-counts')
    client.createSession(username, password)
    return client


SESSION_REQUEST_TIME = Summary(
    'omero_sessions_processing_seconds', 'Time spent counting sessions')


class CountMetrics(object):

    lastusers = set()
    g_last_login = Gauge('omero_counts_agent_login_time',
                         'Time of last Prometheus agent login')
    g_object_counts = Gauge(
        'omero_objects_total', 'Number of OMERO objects',
        ['object', 'group'])

    objtypes = (
        'Screen',
        'Plate',
        'Well',
        'Project',
        'Dataset',
        'Image',
    )

    def __init__(self, client, verbose=False):
        self.client = client
        self.verbose = verbose
        self.g_last_login.set_to_current_time()

    def _count_objects(self, objtype):
        qs = self.client.getSession().getQueryService()
        res = qs.projection(
            'SELECT details.group.name, COUNT(*) FROM %s '
            'GROUP BY details.group.name' % objtype,
            None, {'omero.group': '-1'})
        counts = dict((unwrap(r[0]), unwrap(r[1])) for r in res)
        return counts

    @SESSION_REQUEST_TIME.time()
    def update(self):
        for objtype in self.objtypes:
            counts = self._count_objects(objtype)
            for (group, n) in counts.items():
                self.g_object_counts.labels(objtype, group).set(n)
            if self.verbose:
                print('%s count per group: %s' % (objtype, counts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-u', '--user', default='guest')
    parser.add_argument('-w', '--password', default='guest')
    parser.add_argument('-l', '--listen', type=int, required=True,
                        help='Serve metrics on this port (required)')
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Interval (seconds) between updates, default 60')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    args = parser.parse_args()

    client = connect(args.host, args.user, args.password)
    # Don't catch exception, exit on login failure so user knows

    try:
        # Start up the server to expose the metrics.
        start_http_server(args.listen)
        metrics = CountMetrics(client, verbose=args.verbose)
        while True:
            metrics.update()
            sleep(args.interval)
    finally:
        client.closeSession()
