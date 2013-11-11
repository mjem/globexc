#!/usr/bin/env python

"""Dist configuration file for globexc.
"""

from distutils.core import setup

from globexc import __version__

with open('README.rst') as f:
	readme = f.read()

with open('ChangeLog.rst') as f:
	history = f.read()

setup(name='globexc',
	  version=__version__,
	  description='Write a detailed stack trace if a program crashes',
	  long_description='{readme}\n{history}'.format(readme=readme, history=history),
	  author='Mike Elson',
	  author_email='mike.elson@gmail.com',
	  url='http://github.com/mjem/globexc',
	  packages=['globexc'],
	  license='Apache-2',
	  classifiers=[
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: POSIX :: Linux',
		],
	  )
