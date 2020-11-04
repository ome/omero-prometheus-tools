[![OMERO](https://github.com/ome/omero-prometheus-tools/workflows/OMERO/badge.svg)](https://github.com/ome/omero-prometheus-tools/actions)

[![PyPI version](https://badge.fury.io/py/omero-prometheus-tools.svg)](https://badge.fury.io/py/omero-prometheus-tools)

# Tools for monitoring OMERO with Prometheus

This repository is under development.
Breaking changes may be made without warning.

## Installation

    python3 -mvenv /opt/prometheus-omero-tools
    /opt/prometheus-omero-tools/bin/python setup.py install

## Running

    /opt/prometheus-omero-tools/bin/omero-prometheus-tools.py
      -s omero.example.org -u public -w public
      [-c /opt/prometheus-omero-tools/etc/prometheus-omero-counts.yml ...]

Metrics will be published on http://localhost:9449
