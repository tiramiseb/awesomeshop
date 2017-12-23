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
 
Using AwesomeShop
=================

First, create a configuration file.

Locally for development
-----------------------

Example working on Ubuntu 16.04::

    apt-get install mongodb-server npm nodejs-legacy
    npm install bower -g
    ./init_awesomeshop.sh
    ./init_webroot.sh
    source venv/bin/activate
    ./init_database.py
    ./standalone.py
   
For frontend development, you may also want to start the PLIM watcher, to
automatically regenerate the HTML files::

    ./plim_watcher.py

In production
-------------

First, install (and configure) a MongoDB server. Make sure your configuration
file is okay.

You may preferably run Python in a virtualenv. Install the Python modules
described in ``requirements.txt``. For a standard installation, you may
simply use the ``init_awesomeshop.sh`` script.

Afterwards, initialize the web root and the database if needed
(``init_webroot.sh`` and ``init_database.py``) - don't forget the virtualenv
if needed.

Then, serve ``webroot/`` as static files and ``wsgi.app`` on ``/api`` with a
WSGI server...

Example conf for uWSGI::

    [uwsgi]
    chdir = /srv/awesomeshop
    pythonpath = /srv/awesomeshop
    virtualenv = /srv/awesomeshop/venv
    mount = /api=wsgi:app
    manage-script-name = true



Local templates
===============

The parts you may modify locally, to customize the shop, are - at the moment -
limited to the ``LOGO_CONTENT`` and ``HOME_CONTENT`` variables, configured in
``config.py``.

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

Docker image
============

A docker image, generated with the `Dockerfile` in the current directory, is
available on the docker hub under the name `smaccagnoni/awesomeshop`.

For this image to work, you need to provide the container a `config.py` file,
mounted on `/awesomeshop/config.py`. To serve it, you need a reverse proxy,
which will connect to the awesomeshop container on port 3031 using WSGI and
serve it on `/api`.

The awesomeshop image also shares the web root in a volume, on
`/awesomeshop/webroot`.

A NginX configuration can contain the following parameters:
```
    location / {
        root   /awesomeshop/webroot;
    }
    location /api {
        include uwsgi_params;
        uwsgi_pass api:3031;
    }
```

