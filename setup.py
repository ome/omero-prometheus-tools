from setuptools import setup
setup(
    name='omero-prometheus-tools',
    version='0.2.2',
    description='Tools for monitoring OMERO with Prometheus',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
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
        'omero-py>=5.6.0',
        # TODO: Update to current release 0.7.*
        'prometheus-client==0.2.*',
        'PyYAML',
    ],
    python_requires='>=3',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Monitoring',
    ],
    # Allow external access to etc files
    zip_safe=False,
)
