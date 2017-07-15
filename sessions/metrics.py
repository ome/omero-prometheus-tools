#!/usr/bin/env python

import collections
from datetime import datetime
import omero.clients
import omero.cmd
from prometheus_client import (
    Gauge,
    Summary,
    start_http_server,
)
from time import sleep


def connect():
    client = omero.client('idr-next.openmicroscopy.org')
    client.setAgent('prometheus-omero-py')
    client.createSession('public', 'public')
    return client


SESSION_REQUEST_TIME = Summary(
    'omero_sessions_processing_seconds', 'Time spent counting sessions')


@SESSION_REQUEST_TIME.time()
def update(g, lastcounts):
    # https://github.com/openmicroscopy/openmicroscopy/blob/v5.4.0-m1/components/tools/OmeroPy/src/omero/plugins/sessions.py#L714
    print('\n%s' % datetime.now().isoformat())
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
                print('%s: %d' % (missing, 0))
                g.remove(missing)
            return counts
        finally:
            cb.close(True)
    finally:
        client.closeSession()


if __name__ == '__main__':
    lastcounts = {}
    g = Gauge('omero_sessions_active', 'Active OMERO sessions', ['username'])
    # Start up the server to expose the metrics.
    start_http_server(8123)
    # Generate some requests.
    while True:
        lastcounts = update(g, lastcounts)
        sleep(15)
