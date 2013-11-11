#!/usr/bin/env python

"""Test globexc by throwing an exception.
"""

import logging
from argparse import ArgumentParser

from globexc import init_globexc


def error():
	"""Test function, throws an error."""
	# set a local variable so we can test it appears in the dump file
	my_var = 'a test variable'  # (unused var) pylint:disable=W0612
	print(1 / 0)


def main():
	"""Command line entry point."""

	init_globexc()

	parser = ArgumentParser()
	parser.add_argument('--no-error',
						action='store_false',
						help='Do not throw an error')
	parser.add_argument('--no-init-log',
						action='store_false',
						help='Do not initialise logging system')
	parser.add_argument('--basic-log',
						action='store_true',
						help='Use basic log config even if themelog available')

	args = parser.parse_args()

	if args.no_init_log is not False:
		if args.basic_log is not True:
			try:
				import themelog
				themelog.init_log()

			except ImportError:
				logging.basicConfig()

		else:
			logging.basicConfig()

	if args.no_error is not False:
		error()

	parser.exit('The end')

if __name__ == '__main__':
	main()
