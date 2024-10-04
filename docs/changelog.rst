.. _changelog:

=========
Changelog
=========

Version 0.2
===========

Version 0.2.5 (unreleased)
--------------------------

* Add support for version dependent RST prolog. (`#51 <issue51_>`_)
* Fix various mistakes in the documentation. (`#52 <issue52_>`_, `#53 <issue53_>`_, `#55 <issue55_>`_, `#73 <issue73_>`_)
* Move Git repository to `sphinx-contrib/multiversion <repositoryurl_>`_.
* Switch CI to GitHub Actions and fix various code issues. (`#54 <issue54_>`_, `#117 <issue117_>`_, `#118 <issue118_>`_)

Version 0.2.4 (2020-08-12)
--------------------------

* Skip file existence check for the :file:`.` directory. This fixes an issue if the configuration or source directory is in the local path but reported as missing, because ``git cat-file -e`` always reports an error in that case. (`#12 <issue12_>`_)
* Fix file existence check not working on Windows. (`#18 <issue18_>`_, `#19 <issue19_>`_)
* Fix bug in the sphinx extension which tried to load the `conf.py` from the source directory instead of the conf directory. This could lead to problems when the two directories differ. (`#11 <issue11_>`_, `#13 <issue13_>`_)
* Fix wrong import in :file:`__main__.py` that prevented invocation using ``python -m sphinx_multiversion``. (`#23 <issue23_>`_)
* Fix failure to find refs if ``sphinx-multiversion`` was not invoked from the root of the git repository. (`#24 <issue24_>`_, `#25 <issue25_>`_, `#26 <issue26_>`_)
* Resolve issues with Sphinx extensions and Python modules not being reloaded when parsing the different :file:`conf.py` files. Now, each config file is parsed in it's own process, and the build is performed using the ``subprocess`` module instead of doing it all from the context of the main module. Python's `interpreter flags <pythonflags_>`_ (e.g. isolated mode) are passed through to the subprocesses. (`#22 <issue22_>`_, `#28 <issue28_>`_, `#30 <issue30_>`_, `#36 <issue36_>`_)
* Rewrite the path handling of the Sphinx extension to handle branch names containing a forward slash properly on Windows and add unittests and Windows CI builds to make sure it doesn't break on future updates. (`#31 <issue31_>`_, `#35 <issue35_>`_)


Version 0.2.3 (2020-05-04)
--------------------------

* Fixed return codes of main() function and exit with non-zero status if no matching refs were found.
* Added some logging calls to the git module.
* Fixed bug where local branch was used to check the existence of files on remote branches.


Version 0.2.2 (2020-05-01)
--------------------------

* Added additional checks to determine if a branch or tag contains both the Sphinx source directory and the :file:`conf.py` file. If that's not the case, that branch or tag is skipped automatically and not copied to the temporary directory. (`#9 <issue9_>`_)


Version 0.2.1 (2020-04-19)
--------------------------

* Fixed handling of absolute output paths in `vpathto` and ensure that all generated paths are relative.


Version 0.2.0 (2020-04-19)
--------------------------

* Added a way to override config variables using placeholders that expand to each version's actual value (`#4 <issue4_>`_, `#7 <issue7_>`_).


Version 0.1
===========

Version 0.1.1 (2020-03-12)
--------------------------

* Fixed version number in documentation
* Fixed issue that caused the wrong configuration directory being used when the ``-c`` argument was not specified on the command line

Version 0.1.0 (2020-03-11)
--------------------------

* Initial release


.. _issue4: https://github.com/sphinx-contrib/multiversion/issues/4
.. _issue7: https://github.com/sphinx-contrib/multiversion/issues/7
.. _issue9: https://github.com/sphinx-contrib/multiversion/issues/9
.. _issue11: https://github.com/sphinx-contrib/multiversion/issues/11
.. _issue12: https://github.com/sphinx-contrib/multiversion/issues/12
.. _issue13: https://github.com/sphinx-contrib/multiversion/issues/13
.. _issue18: https://github.com/sphinx-contrib/multiversion/issues/18
.. _issue19: https://github.com/sphinx-contrib/multiversion/issues/19
.. _issue22: https://github.com/sphinx-contrib/multiversion/issues/22
.. _issue23: https://github.com/sphinx-contrib/multiversion/issues/23
.. _issue24: https://github.com/sphinx-contrib/multiversion/issues/24
.. _issue25: https://github.com/sphinx-contrib/multiversion/issues/25
.. _issue26: https://github.com/sphinx-contrib/multiversion/issues/26
.. _issue28: https://github.com/sphinx-contrib/multiversion/issues/28
.. _issue30: https://github.com/sphinx-contrib/multiversion/issues/30
.. _issue31: https://github.com/sphinx-contrib/multiversion/issues/31
.. _issue35: https://github.com/sphinx-contrib/multiversion/issues/35
.. _issue36: https://github.com/sphinx-contrib/multiversion/issues/36
.. _issue51: https://github.com/sphinx-contrib/multiversion/issues/51
.. _issue52: https://github.com/sphinx-contrib/multiversion/issues/52
.. _issue53: https://github.com/sphinx-contrib/multiversion/issues/53
.. _issue55: https://github.com/sphinx-contrib/multiversion/issues/55
.. _issue73: https://github.com/sphinx-contrib/multiversion/issues/73
.. _issue54: https://github.com/sphinx-contrib/multiversion/issues/54
.. _issue117: https://github.com/sphinx-contrib/multiversion/issues/117
.. _issue118: https://github.com/sphinx-contrib/multiversion/issues/118

.. _pythonflags: https://docs.python.org/3/using/cmdline.html#miscellaneous-options
.. _repositoryurl: https://github.com/sphinx-contrib/multiversion
