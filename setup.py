#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pymining',
    version='0.2',
    description='Small collection of data mining algorithms',
    long_description='''
pymining is a small collection of data mining algorithms implemented in Python
(no C extension). This is mainly useful for environments without support for C.

All algorithms come from the scientific literature.
      ''',
    author='Barthelemy Dagenais',
    author_email='barthe@users.sourceforge.net',
    license='BSD License',
    url='https://github.com/bartdag/pymining',
    packages=['pymining'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries',
    ],
)
