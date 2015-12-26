===========
AwesomeShop
===========

AwesomeShop is an e-boutique webapp written in Python with the following
dependencies:

Python dependencies installed with pip:

* *Flask*: web framework
* *Flask-RESTful*: serving the API
* *Marshmallow*: objects transformation for the API
* *MongoDB*: data storage
* *PayPlug*: online credit card payment
* *Pillow*: images manipulation
* *Satchless*: cart and stuff
* *Scrypt*: passwords hashing
* *Whoosh*: indexing and search engine

Front-end libraries/frameworks included:

* `AngularJS <https://angularjs.org/>`_
* some Angular additional modules
* `Bootstrap <http://getbootstrap.com/>`_
* `Font Awesome <http://fontawesome.io/>`_
* `Start Bootstap Simple Sidebar <http://startbootstrap.com/template-overviews/simple-sidebar/>`_

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

This name is only because this app is awesome :)

Licensing
---------

GNU AGPL v3. You can take it, you can use it, you can modify it. But if you
modify it, you must share your modifications. See ``COPYING``. Thanks!

Configuration
=============

Create a ``config.py`` file at the root of the project (in the same directory
as ``run.py``). Take needed directives from ``awesomeshop/defaultconfig.py``.
Any directive defined in ``config.py`` will override the equivalent in
``awesomeshop/defaultconfig.py``.
 
Locally using AwesomeShop
=========================

Example working on Ubuntu 15.10::

    apt-get install mongodb-server
    ./init_pythonapp.sh
    source venv/bin/activate
    ./init_database.py
    ./init_searchindex.py
    ./run.py

When run locally, the Flask debug toolbar extension is enabled (see in
``run.py``).

Local templates
===============

Once run locally, access the shop's homepage: the list of nearly-mandatory
templates is given there.

Deploying in production
=======================

For production deployment, refer to any good Flask WSGI deployment manual.
