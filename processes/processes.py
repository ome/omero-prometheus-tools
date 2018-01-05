#!/usr/bin/env python

import psutil
import sys


class ProcessCounter(object):
    def __init__(self):
        self.np = 0
        self.nt = 0
        self.pset = set()
        self.pnames = dict()

    def addprocess(self, p):
        if p.pid in self.pset:
            return
        self.np += 1
        self.nt += p.num_threads()
        self.pset.add(p.pid)
        print p.name(), p.num_threads()
        try:
            self.pnames[p.name()] += 1
        except KeyError:
            self.pnames[p.name()] = 1
        for c in p.children():
            self.addprocess(c)


def web():
    cmdlines = (
        ['/opt/omero/web/venv/bin/python',
         '/opt/omero/web/OMERO.web/bin/omero'],
        ['/opt/omero/web/venv/bin/python',
         '/opt/omero/web/venv/bin/gunicorn'],
    )
    pc = ProcessCounter()
    for p in psutil.process_iter():
        for cmdline in cmdlines:
            if p.cmdline()[:len(cmdline)] == cmdline:
                pc.addprocess(p)
    print 'TOTAL: processes:{0} threads:{1}, names:{2}'.format(
        pc.np, pc.nt, pc.pnames)


def user(username):
    # This only checks the username of the top parent process
    pc = ProcessCounter()
    for p in psutil.process_iter():
        if p.username() == username:
            pc.addprocess(p)
    print 'TOTAL: processes:{0} threads:{1}, names:{2}'.format(
        pc.np, pc.nt, pc.pnames)

if __name__ == '__main__':
    for u in sys.argv[1:]:
        user(u)
