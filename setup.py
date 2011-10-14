from distutils.core import setup
from setuptools import find_packages
import os
import sys

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def find_packages_in(where, **kwargs):
    return [where] + ['%s.%s' % (where, package) for package in find_packages(where=where, **kwargs)]

setup(
    name = 'django-backup',
    version = '0.0.1',
    author = 'Allan Lei',
    author_email = 'allanlei@helveticode.com',
    description = ('Backup for Django'),
    license = 'New BSD',
    keywords = 'pdf utils django',
    url = 'https://github.com/allanlei/django-backup',
    packages=find_packages_in('backup'),
    long_description=read('README'),
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
