#!/usr/bin/env python

import argparse
import omero.clients

from prometheus_client import (
    Gauge,
    start_http_server,
)
from time import (
    sleep,
    time,
)
from omero_prometheus_tools import (
    CountMetrics,
    SessionMetrics,
)


def connect(hostname, username, password):
    client = omero.client(hostname)
    client.setAgent('prometheus-omero-tools')
    client.createSession(username, password)
    return client


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='append',
                        help='Query configuration files')
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-u', '--user', default='guest')
    parser.add_argument('-w', '--password', default='guest')
    parser.add_argument('-l', '--listen', type=int, default=9449,
                        help='Serve metrics on this port')
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Interval (seconds) between updates, default 60')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    args = parser.parse_args()

    g_last_login = Gauge('omero_prometheus_tools_agent_login_time',
                         'Time of last Prometheus agent login')

    client = connect(args.host, args.user, args.password)
    # Don't catch exception, exit on login failure so user knows
    g_last_login.set_to_current_time()

    try:
        # Start up the server to expose the metrics.
        start_http_server(args.listen)
        if args.config:
            counts = CountMetrics(client, args.config, args.verbose)
        else:
            counts = None
        sessions = SessionMetrics(client, verbose=args.verbose)
        while True:
            starttm = time()
            sessions.update()
            if counts:
                counts.update()
            endtm = time()
            # HQL queries may take a long time
            sleep(max(args.interval + endtm - starttm, 0))
    finally:
        client.closeSession()
