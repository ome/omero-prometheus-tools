FROM continuumio/miniconda3:4.7.12-alpine

RUN /opt/conda/bin/conda install -y -q -c ome omero-py nomkl

COPY *.py /opt/omero-prometheus-tools/
COPY omero_prometheus_tools /opt/omero-prometheus-tools/omero_prometheus_tools/
COPY etc /opt/omero-prometheus-tools/etc/
RUN cd /opt/omero-prometheus-tools/ && \
    /opt/conda/bin/pip install .
ENTRYPOINT ["/opt/conda/bin/omero-prometheus-tools.py"]
