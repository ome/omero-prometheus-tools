#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen

r = urlopen('http://localhost:9449')
rsp = r.read().decode('utf-8')
vals = dict(line.rsplit(' ', 1) for line in rsp.splitlines()
            if not line.startswith('#'))

assert vals['omero_groups_total'] == '4.0'
assert vals['omero_sessions_active{username="test-user"}'] == '1.0'
assert (vals['omero_counts_projects_total{group="بيئة مجهرية مفتوحة"}'] ==
        '1.0')

print('PASSED')
