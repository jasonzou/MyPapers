
========================================================
Notice: This project is still under heavy construction. 
========================================================

MyPapers is an open-source personal paper management system. It makes 
easy to create and manage collections of papers including  bibliographic 
information, some personal information, and fulltext of the papers. MyPapers
is based on BibServer (http://bibserver.okfn.org).

Main features:

* Create and manage bibliographic collections simply and easily
* Import (and export) your collection from bibtex, MARC, RIS, BibJSON, RDF or
  other bibliogrpaphic formats in a matter of seconds
* Browse collection via an elegant faceted interface
* Embed the collection browser in other websites
* Full RESTful API
* Open-source and free to use



Quick Links
===========

* Website: http://
* Code: http://github.com/jasonzou/MyPapers
* Documentation: http://mypapers.readthedocs.org/




Installation
============

See doc/install.rst or
http://mypapers.readthedocs.org/en/latest/install.html


Command Line Usage
==================

Command link script in `cli.py`. To see commands do::

  ./cli.py -h


Developers
==========

To run the tests:

1. Install nose (python-nose)
2. Run the following command::

    nosetests -v test/


Copyright and License
=====================

Copyright?

Licensed under the MIT license



Vendor packages
===============

This MyPapers repository also includes the following vendor packages, all of 
which are javascript plugins available under open source license:

* http://jquery.com
* http://jqueryui.com
* http://twitter.github.com/bootstrap
* http://github.com/okfn/facetview
* http://d3js.org
* http://code.google.com/p/jquery-linkify/

