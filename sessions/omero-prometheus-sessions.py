#!/usr/bin/env python

import argparse
import collections
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
    client.setAgent('prometheus-omero-sessions')
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

    g_users_total = Gauge('omero_users_total', 'Number of OMERO users',
                          ['active'])
    g_groups_total = Gauge('omero_groups_total', 'Number of OMERO groups')

    def __init__(self, client, verbose=False):
        self.client = client
        self.verbose = verbose
        self.g_last_login.set_to_current_time()

    @SESSION_REQUEST_TIME.time()
    def update(self):
        # https://github.com/openmicroscopy/openmicroscopy/blob/v5.4.0-m1/components/tools/OmeroPy/src/omero/plugins/sessions.py#L714

        cb = None
        try:
            cb = self.client.submit(
                omero.cmd.CurrentSessionsRequest(), 60, 500)
            rsp = cb.loop(60, 500)
            counts = collections.Counter(c.userName for c in rsp.contexts)
            missing = self.lastusers.difference(counts.keys())
            for m in missing:
                if self.verbose:
                    print('%s: %d' % (m, 0))
                self.g_sessions.labels(m).set(0)
            for username, n in counts.iteritems():
                if self.verbose:
                    print('%s: %d' % (username, n))
                self.g_sessions.labels(username).set(n)
                self.lastusers.add(username)
        except omero.CmdError as ce:
            # Unwrap the CmdError due to failonerror=True
            raise Exception(ce.err)
        finally:
            if cb:
                cb.close(True)

        adminservice = self.client.getSession().getAdminService()

        user_group_id = adminservice.getSecurityRoles().userGroupId
        users_active = 0
        users_inactive = 0
        for user in adminservice.lookupExperimenters():
            if user_group_id in (unwrap(g.getId()) for g in
                                 user.linkedExperimenterGroupList()):
                users_active += 1
            else:
                users_inactive += 1
        self.g_users_total.labels(1).set(users_active)
        self.g_users_total.labels(0).set(users_inactive)

        group_count = len(adminservice.lookupGroups())
        self.g_groups_total.set(group_count)

        if self.verbose:
            print('Users (active/inactive): %d/%d' % (
                users_active, users_inactive))
            print('Groups: %d' % group_count)


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
        metrics = SessionMetrics(client, verbose=args.verbose)
        while True:
            metrics.update()
            sleep(args.interval)
    finally:
        client.closeSession()
