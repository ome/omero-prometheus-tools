from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.0.1',
    scripts=[
        'sessions/omero-prometheus-sessions.py',
        'counts/omero-prometheus-counts.py',
    ],
    data_files=[
        ('etc', [
            'etc/prometheus-omero-sessions.service',
            'etc/prometheus-omero-counts.service',
            'etc/prometheus-omero-counts.yml',
        ]),
    ],
    install_requires=[
        'prometheus-client>=0.2,<0.3',
    ],
    # Allow external access to etc files
    zip_safe=False,
)
