# Tools for monitoring OMERO with Prometheus

This repository is under development.
Breaking changes may be made without warning.

## Installation

    virtualenv /opt/prometheus-omero-tools
    /opt/prometheus-omero-tools/bin/python setup.py install

Install OMERO.py into the virtualenv.

## Running

    /opt/prometheus-omero-tools/bin/omero-prometheus-tools.py
      -s omero.example.org -u public -w public
      [-c /opt/prometheus-omero-tools/etc/prometheus-omero-counts.yml ...]

Metrics will be published on http://localhost:9449
