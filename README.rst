===========
AwesomeShop
===========

AwesomeShop is a light and fast e-boutique webapp, using modern techniques
to achieve these goals.

AwesomeShop is written in Javascript/AngularJS and Python.

AweshomeShop uses the following awesome tools:

* webpages serving and API interface: Flask with Flask-RESTful, Marshmallow...
* data storage: MongoDB, MongoEngine...
* frontend: AngularJS, Bootstrap, FontAwesome...
* and much more libraries, thanks to all their authors!

General information
===================

Contributions
-------------

This tool is first made for the Domotego online shop. But any contribution is
accepted, even if it would not be used by Domotego.

Pull requests are welcome. Your code should be clean to be accepted in the main
repository. And don't forget PEP 8!

Name
----

Not related to *Font-Awesome* in any way... except that it uses it.

This name is only because this app is awesome, as all used modules. The world
is awesome, Open Source is awesome, we are all awesome :)

Licensing
---------

GNU AGPL v3. You can take it, you can use it, you can modify it. But if you
modify it and use it, you must share your modifications. See ``COPYING``.
Thanks!

Configuration
=============

Create a ``config.py`` file at the root of the project (in the same directory
as ``standalone.py``). Take needed directives from ``back/defaultconfig.py``.
Any directive defined in ``config.py`` will override the equivalent in
``back/defaultconfig.py``.
 
Locally using AwesomeShop
=========================

Example working on Ubuntu 16.04::

    apt-get install mongodb-server
    ./init_awesomeshop.sh
    source venv/bin/activate
    ./init_webroot.py
    ./init_database.py
    ./standalone.py

Local templates
===============

Once run locally, access the shop's homepage: the list of nearly-mandatory
templates is given there.

Using reStructuredText
======================

All text is in the reStructuredText format. There are two specific behaviors...

Use the following directive to include a list of all documentation pages::

    .. doc-list::

Use the following format to include a link to a(nother) page::

    [pageslug]

or::

    [displayed text|pageslug]

Deploying in production
=======================

For production deployment, refer to any good Flask WSGI deployment manual.
