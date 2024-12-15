FROM continuumio/miniconda3:24.9.2-0 as builder

USER root

COPY . /omero-prometheus-tools/
RUN cd /omero-prometheus-tools/ && \
     /opt/conda/bin/python -mpip install build && \
    /opt/conda/bin/python -m build

######################################################################

FROM continuumio/miniconda3:24.9.2-0
# https://jcrist.github.io/conda-docker-tips.html
RUN /opt/conda/bin/pip install https://github.com/glencoesoftware/zeroc-ice-py-linux-x86_64/releases/download/20240202/zeroc_ice-3.6.5-cp312-cp312-manylinux_2_28_x86_64.whl
RUN /opt/conda/bin/pip install omero-py
RUN /opt/conda/bin/conda install -y -q -c conda-forge nomkl

COPY --from=builder /omero-prometheus-tools/dist/*.whl .
RUN /opt/conda/bin/pip install *.whl
ENTRYPOINT ["/opt/conda/bin/omero-prometheus-tools.py"]
