from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-datapusher',
    version=version,
    description="Backport of ckanext-datapusher for ckan 2.1",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='OKFN',
    author_email='david.raznick@okfn.org',
    url='http://ckan.org',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.datapusherext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        datapusherext=ckanext.datapusherext.plugin:DatapusherPlugin
    ''',
)
