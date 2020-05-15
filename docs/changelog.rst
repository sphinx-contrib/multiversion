.. _changelog:

=========
Changelog
=========

Version 0.2
===========

Version 0.2.4 (unreleased)
--------------------------

* Skip file existence check for the :file:`.` directory. This fixes an issue if the configuration or source directory is in the local path but reported as missing, because ``git cat-file -e`` always reports an error in that case. (`#12 <issue12_>`_)
* Fix bug in the sphinx extension which tried to load the `conf.py` from the source directory instead of the conf directory. This could lead to problems when the two directories differ. (`#11 <issue11_>`_, `#13 <issue11_>`_)


Version 0.2.3
-------------

* Fixed return codes of main() function and exit with non-zero status if no matching refs were found.
* Added some logging calls to the git module.
* Fixed bug where local branch was used to check the existence of files on remote branches.


Version 0.2.2
-------------

* Added additional checks to determine if a branch or tag contains both the Sphinx source directory and the :file:`conf.py` file. If that's not the case, that branch or tag is skipped automatically and not copied to the temporary directory. (`#9 <issue9_>`_)


Version 0.2.1
-------------

* Fixed handling of absolute output paths in `vpathto` and ensure that all generated paths are relative.


Version 0.2.0
-------------

* Added a way to override config variables using placeholders that expand to each version's actual value (`#4 <issue4_>`_, `#7 <issue7_>`_).


Version 0.1
===========

Version 0.1.1
-------------

* Fixed version number in documentation
* Fixed issue that caused the wrong configuration directory being used when the ``-c`` arguement was not specified on the command line

Version 0.1.0
-------------

* Initial release


.. _issue4: https://github.com/Holzhaus/sphinx-multiversion/issues/4
.. _issue7: https://github.com/Holzhaus/sphinx-multiversion/issues/7
.. _issue9: https://github.com/Holzhaus/sphinx-multiversion/issues/9
.. _issue11: https://github.com/Holzhaus/sphinx-multiversion/issues/11
.. _issue12: https://github.com/Holzhaus/sphinx-multiversion/issues/12
.. _issue13: https://github.com/Holzhaus/sphinx-multiversion/issues/13
