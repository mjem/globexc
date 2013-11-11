globexc
=======

Introduction
------------

globexc is a library which makes the Python interpreter write a detailed stack trace if an unhandled exception occurs in a script. This trace is written to a separate file and includes, for each level of the stack, the values of local variables and a few lines of context code. This allows the developer to perform a basic post-mortem analysis of an error without having to recreate the scenario inside a debugger or using verbose logging.

The output is similar to the in-browser stack trace given by the Werkzeug or Django web frameworks but available to any Python program even if it's not a web server. 

Example
-------

To generate a stack trace:

  .. code:: python

	import globexc

	# install the exception handler
	globexc.init_globexc()

	# cause an unhandled exception
	a = 1 / 0

And the resulting terminal output:

  .. code::

	CRITICAL Exception <type 'exceptions.ZeroDivisionError'> (tests/sample.py:15) integer
	division or modulo by zero. Trace file written to '/home/user/trace.dump'.

And for the stack trace see `<extra/trace.dump>`_.

Installation
------------

Install using setuptools:

  .. code:: sh

	python setup.py build
	python setup.py install

Or from pypi:

  .. code:: sh

	pip install globexc

Usage
-----

Call ``init_globexc()`` during program startup to install the global exception handler. The stack trace will then be generated when any unhandled exception occurs. The output works whether or not the Python logging system has been initialised.

Environment variables
---------------------

You can set the following environment variable to configure the library:

**GLOBEXC**
  Choose an alternative filename for stack traces.

Requirements
------------

None

Compatibility
-------------

This code has been tested under Linux and using Python 2.7 only.

Legal
-----

globexc is copyright 2013 Mike Elson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
