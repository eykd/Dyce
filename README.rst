==================
 Welcome to Dyce!
==================

Dyce is a toolkit for rolling dice. It's a friendly wrapper around
python's random module.

Dyce also has a mini-language for expressing random number patterns,
including common dice notation, making it ideal for easily storing
random number generators in config files.

Dyce has been tested on python 2.4 and 2.5. It will probably work on
2.6. Please let me know if you have any trouble with it.

David Eyk
eykd@eykd.net


Installation
============

Install Dyce using the standard distutils method::

  $ python setup.py install

Dyce can also be installed with pip or easy_install::

  $ pip install Dyce

or::

  $ easy_install Dyce


Documentation
=============

API documentation can be found at <http://worlds.eykd.net/dyce/api/>.

For more information about Dyce, please visit the project site at
<https://github.com/eykd/dyce>.


Development and Testing
=======================

To develop and test Dyce, use `Paver
<http://paver.github.com/paver/>`_ to set up your virtual environment:

With Paver::

  $ paver env
  $ source bin/activate
  $ paver test

From scratch::

  $ python bootstrap.py
  $ source bin/activate
  $ paver test

Hopefully, you'll find Dyce easy to work with and adapt.
