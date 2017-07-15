FROM centos:7

RUN yum install -y -q epel-release && \
    yum install -y -q python-pip && \
    pip install https://github.com/openmicroscopy/zeroc-ice-py-centos7/releases/download/0.0.2/zeroc_ice-3.6.3-cp27-cp27mu-linux_x86_64.whl

RUN pip install omego && \
    mkdir -p /opt/omero && \
    cd /opt/omero && \
    omego download python --sym OMERO.py

RUN pip install prometheus_client && \
    mkdir -p /opt/prometheus-omero-py/ && \
    curl -so /opt/prometheus-omero-py/metrics.py https://gist.githubusercontent.com/manics/238a63cfd9c2fb8a450252d79e609296/raw/b0ed1edcf662415339d786aeb764c8056386e1a5/metrics.py

ENV PYTHONPATH=/opt/omero/OMERO.py/lib/python
ENTRYPOINT ["python", "/opt/prometheus-omero-py/metrics.py", "--listen", "8000"]
EXPOSE 8000
