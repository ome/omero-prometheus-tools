FROM continuumio/miniconda3:4.7.12-alpine as builder

USER root

COPY . /omero-prometheus-tools/
RUN cd /omero-prometheus-tools/ && \
    /opt/conda/bin/python setup.py sdist bdist_wheel

######################################################################

FROM continuumio/miniconda3:4.7.12-alpine
# https://jcrist.github.io/conda-docker-tips.html
RUN /opt/conda/bin/conda install -y -q -c conda-forge omero-py nomkl
COPY --from=builder /omero-prometheus-tools/dist/*.whl .
RUN /opt/conda/bin/pip install *.whl
ENTRYPOINT ["/opt/conda/bin/omero-prometheus-tools.py"]
