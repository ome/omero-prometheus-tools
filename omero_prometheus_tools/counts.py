#!/usr/bin/env python

import omero.clients
from omero.rtypes import unwrap

from prometheus_client import (
    Gauge,
    Summary,
)
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
        # HQL count won't return 0 so need to explicitly delete labelsets
        self.labelsets = set()

    def update(self, queryservice):
        results = queryservice.projection(
            self.query, None, {'omero.group': '-1'})
        if not results:
            if self.verbose:
                print('%s NULL' % self.name)
        prev_labelsets = self.labelsets
        self.labelsets = set()
        for r in results:
            labelvalues = [lv for lv in unwrap(r[1:])]
            value = unwrap(r[0])
            self.prometheus_gauge.labels(*labelvalues).set(value)
            self.labelsets.add(tuple(labelvalues))
            if self.verbose:
                print('%s %s %s' % (self.name, labelvalues, value))
        # Now delete absent labelsets
        for rm in prev_labelsets.difference(self.labelsets):
            self.prometheus_gauge.remove(*rm)
            if self.verbose:
                print('Removed %s %s' % (self.name, rm))


class CountMetrics(object):

    def __init__(self, client, configfiles, verbose=False):
        self.client = client
        self.verbose = verbose

        self.metrics = {}
        for f in configfiles:
            with open(f) as fh:
                cfg = yaml.load(fh, Loader=yaml.FullLoader)
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
