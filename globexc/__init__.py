#!/usr/bin/env python

"""Global exception handling code. When an unhandled exception occurs we log a brief
message and also print a full stack trace including local variable contents.
"""

from __future__ import print_function
from __future__ import unicode_literals

__version__ = '0.1.1'

import os
import sys
import types
import logging

# logger to use to write a brief message on unhandled exception
logger = logging.getLogger('globexc')

# indentation inside trace file
INDENTATION = '  '

# location to store stack trace
DEFAULT_STACK_TRACE_FILENAME = 'trace.dump'

# environment variable to check for an overridden stack trace filename
ENV_STACK_TRACE_FILENAME = 'GLOBEXC'

# additional lines to show before/after current line
CONTEXT_LINES = 4


def expanded_filename():
	"""Return the full absolute path to the STACK_TRACE_FILENAME with any environment
	variables ($VAR) and users (~user) expanded."""
	return os.path.abspath(
		os.path.expanduser(
			os.path.expandvars(
				os.getenv(ENV_STACK_TRACE_FILENAME, DEFAULT_STACK_TRACE_FILENAME))))


def display_tb(tb, indent='', depth=1, target=sys.stdout):
	"""Print information from a traceback (=one frame of a stack trace),
	and recursively call ourselves to display the next frame."""
	if tb.tb_next is not None:
		# recursion - display the next traceback down the stack,
		# before displaying this one
		display_tb(tb.tb_next, indent=indent, depth=depth + 1, target=target)

	target.write('{indent}Frame {depth}:\n'.format(indent=indent, depth=depth))

	# show context - a few lines of code either side of the line emitting the exception
	display_code(tb.tb_frame.f_code.co_filename,
				 tb.tb_lineno,
				 indent=indent + INDENTATION,
				 target=target)
	target.write('\n')

	# show local variable values
	display_locals(tb.tb_frame.f_locals,
				   indent=indent + INDENTATION,
				   target=target)
	target.write('\n')


def display_locals(f_locals, indent='', target=sys.stdout):
	"""Print a list of local variables from a stack frame.
	Exclude:
	 - Hidden variables starting with '__'
	 - Type definitions
	 - Modules
	 - Functions
	 - Class methods
	 - Class member variables, if called from a member function
	 - variables called "password"
	 """

	target.write(indent + 'Vars:\n')
	# from django.core.handlers.wsgi import WSGIRequest
	value = None
	for k, v in f_locals.iteritems():
		# don't bother displaying vars with names like '__*' or local function definitions
		if (k.startswith('__') or
			k in ('environ',  # probably contains full shell environment
				  'self',  # don't bother showing members variables as usually too verbose
				  'password') or  # try not to write passwords to trace
			isinstance(v, (
					# WSGIRequest,
					types.TypeType,  # hide things that usually exist in locals() just
					types.ModuleType,  # because they were imported
					types.FunctionType,
					types.MethodType,
					))):

			continue

		# unicode(v) may appear unnecessary but is needed if a stack frame contains a
		# listiterator as a local variable since str.format() calls __format__
		# on the bind variables, not __str__/__unicode__.
		try:
			value = unicode(v)
		except Exception:  # (no exception type) pylint:disable=W0703
			# we have to trap all exceptions here since str()/unicode() could throw anything
			# and result in a confused stack trace irrelevant to the original error
			value = '<error>'

		# surround actual string values with quotes
			# (throws error if given bytestring)
		# if isinstance(v, basestring):
			# v = '"{v}"'.format(v=v)

		target.write('{indent_}{name} = {value} ({dtype})\n'.format(
				indent_=indent + INDENTATION,
				dtype=str(type(v))[7:-2],  # !
				name=k,
				value=value))

	if value is None:
		target.write('{indent_}<none>'.format(indent_=indent + INDENTATION))


def display_code(filename, lineno, indent='', target=sys.stdout):
	"""Display CONTEXT_LINES lines of code in `filename` around `lineno`."""
	if not os.path.isfile(filename):
		target.write('{indent}File {filename} not found\n\n'.format(
				indent=indent,
				filename=filename))
		return

	target.write('{indent}Filename:\n'
				 '{indent_}{filename}\n'
				 '\n'
				 '{indent}Code:\n'.format(
			indent=indent,
			indent_=indent + INDENTATION,
			filename=filename))

	for i, line in enumerate(open(filename, 'r'), start=1):
		if i > (lineno + CONTEXT_LINES):
			break

		if i < (lineno - CONTEXT_LINES):
			continue

		target.write('{indent}{mark}{lineno:5}: {code}'.format(
				indent=indent,
				lineno=i,
				code=line.replace('\t', '    '),
				mark='->' if i == lineno else '  '))


def global_exception(exc_type, exc_value, exc_traceback):
	"""Entry point for unhandled exceptions.."""

	# Walk to the end of the stack trace to find the line that actually raised the exception
	acc = exc_traceback
	while acc is not None:
		filename = acc.tb_frame.f_code.co_filename
		lineno = acc.tb_lineno
		acc = acc.tb_next

	# Print a brief summary of the exception to the log.
	# We suppress this if the exception was broken pipe because there is a good
	# change all that happened is the user was piping to more/less and pressed 'q'
	if not (exc_type is IOError and exc_value.errno == 32):
		logger.critical('Exception {cls} ({filename}:{lineno}) {message}. '
						'Trace file written to \'{trace}\'.'.format(
				cls=exc_type,
				# cls=str(exc_type).replace('<class \'', '').replace('\'>', ''),
				message=unicode(exc_value),
				filename=filename,
				lineno=lineno,
				trace=expanded_filename()))
		# be very paranoid here as we are reading undocumented attributes of logging
		if hasattr(logger, 'manager') and \
				getattr(logger.manager, 'emittedNoHandlerWarning') is True:
			# make sure the user sees something even if logging is not initialised
			# (as of python 2.7.5 the logging module suppresses all output if not
			# initialised
			print('Trace file written to {trace}'.format(
					trace=expanded_filename()))

	# Print an even briefer version to stderr if it is an interactive terminal
	if sys.stderr.isatty():
		print('\n{message}\n'.format(message=str(exc_value)))

	# Now write a full dump and stack trace to the trace file
	with open(expanded_filename(), 'w') as h:
		h.write('Exception object:\n'
				'{indent}Class: {cls}\n'
				'{indent}Text: {value}\n'
				'{indent}Attributes:\n'.format(
				# cls=str(exc_type).replace('<class \'', '').replace('<type \'', '').replace(
					# '\'>', ''),
				cls=exc_type,
				value=exc_value,
				indent=INDENTATION))
		# list all the attributes of the exception object
		for key in dir(exc_value):
			if not key.startswith('_'):
				h.write('{indent}{indent}{key}: {value}\n'.format(
						indent=INDENTATION, key=key, value=getattr(exc_value, key)))

		h.write('\nCall stack:\n')
		display_tb(exc_traceback, indent='  ', target=h)


def init_globexc(filename=None, context=None):
	"""Install our global exception handler.

	Args:
		`filename` (str): Specify filename for stack traces.
		`context` (int): Number of lines of context around the current line in code
			displays.
	"""
	global DEFAULT_STACK_TRACE_FILENAME
	global CONTEXT_LINES

	if filename is not None:
		DEFAULT_STACK_TRACE_FILENAME = filename

	if context is not None:
		CONTEXT_LINES = context

	sys.excepthook = global_exception
