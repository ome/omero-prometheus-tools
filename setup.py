from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.0.1',
    scripts=[
        'sessions/omero-prometheus-sessions.py',
    ],
    data_files=[
        ('service', ['sessions/prometheus-omero-sessions.service']),
    ],
    install_requires=[
        'prometheus-client>=0.2,<0.3',
    ],
    # Allow external access to prometheus-omero-py-metrics.service file
    zip_safe=False,
)
