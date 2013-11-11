#!/usr/bin/env python

"""Utilities for globexc project."""

import os

from fabric.api import local


def clean():
	"""Remove temporary .pyc and pyo files, env and dist directories."""
	clean_py()
	local('rm env -rf')
	local('rm dist -rf')


def sdist():
	"""Make a source distribution."""
	local('python setup.py sdist')


def archive():
	"""Make a tarball of the git source repository."""
	local('tar cf globexc.git.tar.bz2 .git')


def dist():
	"""Make a tarball of the tracked files."""
	local('git archive globexc.tar.bz2')


def pylint():
	"""Run pylint over all files."""
	local('pylint fabfile.py globexc tests')


def pep8():
	"""Run pep8 over all files."""
	local('pep8 fabfile.py globexc tests')


def clean_py():
	"""Remove *.pyc and *.pyo files."""
	# local("find . -name '*.pyo' -exec rm {} \;
	from unipath import Path
	from unipath import FILES
	cc_pyo = 0
	cc_pyc = 0
	print('Looking for .pyo and .pyc files...')
	for f in Path('globexc').walk(filter=FILES):
		if f.ext == '.pyo':
			f.remove()
			cc_pyo += 1

		if f.ext == '.pyc':
			f.remove()
			cc_pyc += 1

	print('Deleted {o} .pyo and {c} .pyc files'.format(o=cc_pyo, c=cc_pyc))


def make_sample():
	"""Recreate the sample extra/trace.dump file."""
	dirname = 'extra'
	filename = 'trace.dump'

	if not os.path.isdir(dirname):
		os.mkdir(dirname)

	# local() checks exit code so we suppress it
	local('GLOBEXC={path} tests/sample.py || true'.format(
			path=os.path.join(dirname, filename)))
