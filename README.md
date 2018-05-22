# Tools for monitoring OMERO with Prometheus

This repository is under development.
Breaking changes may be made without warning.

## Installation

    virtualenv /opt/prometheus-omero-tools
    /opt/prometheus-omero-tools/bin/python setup.py install

Install OMERO.py into the virtualenv.

## Running

    /opt/prometheus-omero-tools/bin/omero-prometheus-sessions.py
      -s omero.example.org -u public -w public -l 9123

Metrics will be published on http://localhost:9123
