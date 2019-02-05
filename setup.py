from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.1.3',
    scripts=[
        'omero_prometheus_tools/omero-prometheus-tools.py',
    ],
    data_files=[
        ('etc', [
            'etc/prometheus-omero-counts.yml',
        ]),
    ],
    packages=[
        'omero_prometheus_tools',
    ],
    install_requires=[
        'prometheus-client>=0.2,<0.3',
        'PyYAML',
    ],
    # Allow external access to etc files
    zip_safe=False,
)
