.. _faq:

==========================
Frequently Asked Questions
==========================

Why another tool for versioning Sphinx docs?
============================================

While there are several sphinx extensions out there (e.g.  `sphinxcontrib-versioning <sphinxcontrib_versioning_>`_  or `sphinx-versions <sphinx_versions_>`_) none of them seem to work correctly with recent sphinx versions (as of March 2020).
Their code heavily relies on monkey-patching Sphinx internals at runtime, which is error-prone and makes the code a mess.

In contrast, the extension part of ``sphinx-multiversion`` does not do any fancy patching, it just provides some HTML context variables.


How does it work?
=================

Instead of running `sphinx build`, just run `sphinx-multiversion` from the root of your Git repository.
It reads your Sphinx :file:`conf.py` file from the currently checked out Git branch for configuration, then generates a list of versions from local or remote tags and branches.
This data is written to a JSON file - if you want to have a look what data will be generated, you can use the ``--dump-metadata`` flag.

Then it copies the data for each version into separate temporary directories, builds the documentation from each of them and writes the output to the output directory.
The :file:`conf.py` file from the currently checked out branch will be used to build old versions, so it's not necessary to make changes old branches or tags to add support for ``sphinx-multiversion``.
This also means that theme improvements, template changes, etc. will automatically be applied to old versions without needing to add commits.


Do I need to make changes to old branches or tags?
==================================================

No, you don't. ``sphinx-multiversion`` will always use the :file:`conf.py` file from your currently checked out branch.

The downside is that this behaviour restricts the kinds of changes you may do to your configuration, because it needs to retain compatibility with old branches.
For example, if your :file:`conf.py` file hardcodes a path (e.g. for opening a file), but that file does not exist in some older branches that you want to build documentation for, this will cause issues.
In these cases you will need to add a check if a file actually exists and adapt the path accordingly.


What are the license terms of ``sphinx-multiversion``?
======================================================

``sphinx-multiversion`` is licensed under the terms of the `BSD 2-Clause license <bsd_2clause_license_>`_.


.. _sphinxcontrib_versioning: https://github.com/sphinx-contrib/sphinxcontrib-versioning
.. _sphinx_versions: https://github.com/Smile-SA/sphinx-versions
.. _bsd_2clause_license: https://choosealicense.com/licenses/bsd-2-clause/
