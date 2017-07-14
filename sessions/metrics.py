#!/usr/bin/env python

import collections
import omero.clients
import omero.cmd
import prometheus_client
import time


def connect():
    client = omero.client('idr-next.openmicroscopy.org')
    client.setAgent('prometheus-omero-py')
    client.createSession('public', 'public')
    return client


def update(g, lastcounts):
    # https://github.com/openmicroscopy/openmicroscopy/blob/v5.4.0-m1/components/tools/OmeroPy/src/omero/plugins/sessions.py#L714
    client = connect()
    try:
        cb = client.submit(omero.cmd.CurrentSessionsRequest())
        try:
            rsp = cb.getResponse()
            counts = collections.Counter(c.userName for c in rsp.contexts)
            for username, n in counts.iteritems():
                print('%s: %d' % (username, n))
                g.labels(username).set(n)
            for missing in set(lastcounts.keys()).difference(counts.keys()):
                print('%s: %d' % (username, 0))
                g.remove(missing)
            lastcounts = counts
        finally:
            cb.close(True)
    finally:
        client.closeSession()


if __name__ == '__main__':
    lastcounts = {}
    g = prometheus_client.Gauge(
        'omero_sessions_active', 'Active OMERO sessions', ['username'])
    # Start up the server to expose the metrics.
    prometheus_client.start_http_server(8123)
    # Generate some requests.
    while True:
        update(g, lastcounts)
        time.sleep(15)
