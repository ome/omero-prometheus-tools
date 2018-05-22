from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.0.1',
    scripts=[
        'sessions/omero-prometheus-sessions.py'
    ],
    install_requires=[
        'prometheus-client>=0.2,<0.3'
    ],
)
