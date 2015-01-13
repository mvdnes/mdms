mdms
====

M's document management system

This project provides a very basic way for storing documents.

A document has the following properties:

* name
* date
* extra information
* some tags
* some files

Usage
-----

Simply start the webserver by running

    python mdms web

Optionally, you can specify the `-d` flag to start in debug mode.

MDMS also supports some other commands. To view which those are, run mdms with `--help`.

Configuration
-------------

In `config.toml` you can specify the location for the database and the documents to be stored.

WSGI
----

The webserver can also be used as a WSGI app. Simply point to the `mdms.wsgi` file.
