from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.0.1',
    scripts=[
        'sessions/omero-prometheus-sessions.py',
        'counts/omero-prometheus-counts.py',
    ],
    data_files=[
        ('service', [
            'service/prometheus-omero-sessions.service',
            'service/prometheus-omero-counts.service',
        ]),
    ],
    install_requires=[
        'prometheus-client>=0.2,<0.3',
    ],
    # Allow external access to prometheus-omero-sessions.service file
    zip_safe=False,
)
