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
from time import sleep, time
import yaml


def connect(hostname, username, password):
    client = omero.client(hostname)
    client.setAgent('prometheus-omero-counts')
    client.createSession(username, password)
    return client


SESSION_REQUEST_TIME = Summary(
    'omero_counts_processing_seconds', 'Time spent counting sessions')


class QueryMetric(object):
    def __init__(self, name, cfg, verbose):
        self.name = name
        description = cfg['description']
        self.query = cfg['query']
        labels = cfg['labels']
        # Let prometheus_client handle name validation
        self.prometheus_gauge = Gauge(self.name, description, labels)
        self.verbose = verbose

    def update(self, queryservice):
        results = queryservice.projection(
            self.query, None, {'omero.group': '-1'})
        if not results:
            if self.verbose:
                print('%s NULL' % self.name)
        for r in results:
            labelvalues = unwrap(r[1:])
            value = unwrap(r[0])
            self.prometheus_gauge.labels(*labelvalues).set(value)
            if self.verbose:
                print('%s %s %s' % (self.name, labelvalues, value))


class CountMetrics(object):

    lastusers = set()
    g_last_login = Gauge('omero_counts_agent_login_time',
                         'Time of last Prometheus agent login')

    def __init__(self, client, configfiles, verbose=False):
        self.client = client
        self.verbose = verbose
        self.g_last_login.set_to_current_time()

        self.metrics = {}
        for f in configfiles:
            with open(f) as fh:
                cfg = yaml.load(fh)
            for name in cfg:
                if name in self.metrics:
                    raise Exception(
                        'Duplicate metric name found: %s' % name)
                self.metrics[name] = QueryMetric(name, cfg[name], verbose)

    @SESSION_REQUEST_TIME.time()
    def update(self):
        queryservice = self.client.getSession().getQueryService()
        for metric in self.metrics.values():
            metric.update(queryservice)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='append',
                        help='Query configuration files')
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
        metrics = CountMetrics(client, args.config, args.verbose)
        while True:
            starttm = time()
            metrics.update()
            endtm = time()
            # HQL queries may take a long time
            sleep(max(args.interval + endtm - starttm, 0))
    finally:
        client.closeSession()
