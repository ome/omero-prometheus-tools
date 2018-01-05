#!/usr/bin/env python

import argparse
from collections import defaultdict
from prometheus_client import (
    Gauge,
    Summary,
    start_http_server,
)
from psutil import process_iter
from time import sleep


PROCESS_REQUEST_TIME = Summary(
    'user_processes_processing_seconds', 'Time spent counting processes')


class ProcessMetrics(object):

    g_processes = Gauge(
        'user_processes', 'Number of processes', ['username', 'procname'])
    g_threads = Gauge(
        'user_threads', 'Number of threads', ['username', 'procname'])

    def __init__(self, usernames, procnames, verbose=False):
        self.usernames = set(usernames)
        self.procnames = set(procnames)
        self.all_procnames = ('*' in self.procnames)
        if self.all_procnames:
            self.procnames.remove('*')
        self.verbose = verbose

    def reset(self):
        self.pset = set()
        self.counts = defaultdict(lambda: [0, 0])

    def addprocess(self, p):
        username = p.username()
        procname = p.name()
        if (p.pid in self.pset or
                (username not in self.usernames) or
                (not self.all_procnames and procname not in self.procnames)):
            return
        name = procname if procname in self.procnames else '*'
        self.counts[(username, name)][0] += 1
        self.counts[(username, name)][1] += p.num_threads()
        self.pset.add(p.pid)
        if self.verbose:
            print('{0} {1} {2}'.format(username, procname, p.num_threads()))

    @PROCESS_REQUEST_TIME.time()
    def update(self):
        self.reset()
        for p in process_iter():
            self.addprocess(p)
        for username in self.usernames:
            for procname in self.procnames:
                k = (username, procname)
                v = self.counts[k]
                self.g_processes.labels(*k).set(v[0])
                self.g_threads.labels(*k).set(v[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--username', action='append', required=True, default=[],
        help='Get processes for this user, can be repeated')
    parser.add_argument(
        '-p', '--procname', action='append', required=True, default=[],
        help='Process name, can be repeated, use * for all')
    parser.add_argument('-l', '--listen', type=int, required=True)
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Interval (seconds) between updates, default 60')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose output')
    args = parser.parse_args()

    # Start up the server to expose the metrics.
    start_http_server(args.listen)
    metrics = ProcessMetrics(
        args.username, args.procname, verbose=args.verbose)
    while True:
        metrics.update()
        sleep(args.interval)
