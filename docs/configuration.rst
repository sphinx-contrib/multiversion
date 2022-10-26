.. _configuration:

=============
Configuration
=============

``sphinx-multiversion`` reads your Sphinx :file:`conf.py` file for configuration.
As usual, you can also override certain options by using ``-D var=value`` on the command line.

This is what the default configuration looks like:

.. code-block:: python

    # Whitelist pattern for tags (set to None to ignore all tags)
    smv_tag_whitelist = r'^.*$'

    # Whitelist pattern for branches (set to None to ignore all branches)
    smv_branch_whitelist = r'^.*$'

    # Whitelist pattern for remotes (set to None to use local branches only)
    smv_remote_whitelist = None

    # Pattern for released versions
    smv_released_pattern = r'^tags/.*$'

    # Format for versioned output directories inside the build directory
    smv_outputdir_format = '{ref.name}'

    # Determines whether remote or local git branches/tags are preferred if their output dirs conflict
    smv_prefer_remote_refs = False

    # Specify build targets and whether the resulting artefacts should be downloadable
    smv_build_targets = {
        "HTML" : {
            "builder": "html",
            "downloadable": False,
            "download_format": "",
        },
    }

    # Flag indicating whether the intermediate build directories should be removed after artefacts are produced
    smv_clean_intermediate_files = True


You can override all of these values inside your :file:`conf.py`.

.. note::

    You can check which tags/branches are matched by running ``sphinx-multiversion`` with the ``--dump-metadata`` flag. Branches or tags that don't contain both the sphinx source directory and the :file:`conf.py` file will be skipped automatically.

Tag/Branch/Remote whitelists
============================

Tags, Branches and Remotes are included by `Regular Expressions <python_regex_>`_.
Here are some examples:

.. code-block:: python

    smv_tag_whitelist = r'^.*$'                   # Include all tags
    smv_tag_whitelist = r'^v\d+\.\d+$'            # Include tags like "v2.1"

    smv_branch_whitelist = r'^.*$'                # Include all branches
    smv_branch_whitelist = r'^(?!master).*$'      # Include all branches except "master"

    smv_remote_whitelist = None                   # Only use local branches
    smv_remote_whitelist = r'^.*$'                # Use branches from all remotes
    smv_remote_whitelist = r'^(origin|upstream)$' # Use branches from origin and upstream

.. note::

    To list values to match, you can use ``git branch``, ``git tag`` and ``git remote``.


Release Pattern
===============

A Regular Expression is used to determine if a version of the documentation has been released or if it's a development version.
To allow more flexibility, the regex is evaluated over the full refname.

Here are some examples:

.. code-block:: python

    smv_released_pattern = r'^tags/.*$'           # Tags only
    smv_released_pattern = r'^heads/\d+\.\d+$'    # Branches like "2.1"
    smv_released_pattern = r'^(tags/.*|heads/\d+\.\d+)$'           # Branches like "2.1" and all tags
    smv_released_pattern = r'^(heads|remotes/[^/]+)/(?!:master).*$' # Everything except master branch

.. note::

    To list all refnames , you can use:

    .. code-block:: bash

        git for-each-ref --format "%(refname)" | sed 's/^refs\///g'


Output Directory Format
=======================

Each version will be built into a seperate subdirectory of the Sphinx output directory.
The ``smv_outputdir_format`` setting determines the directory structure for the subdirectories. It is a new-style Python formatting string with two parameters - ``ref`` and ``config``.

Here are some examples:

.. code-block:: python

    smv_outputdir_format = '{ref.name}'        # Use the branch/tag name
    smv_outputdir_format = '{ref.commit}'      # Use the commit hash
    smv_outputdir_format = '{ref.commit:.7s}'  # Use the commit hash truncated to 7 characters
    smv_outputdir_format = '{ref.refname}'     # Use the full refname
    smv_outputdir_format = '{ref.source}/{ref.name}'      # Equivalent to the previous example
    smv_outputdir_format = 'versions/{config.release}'    # Use "versions" as parent directory and the "release" variable from conf.py
    smv_outputdir_format = '{config.version}/{ref.name}'  # Use the version from conf.py as parent directory and the branch/tag name as subdirectory


.. seealso::

    Have a look at `PyFormat <python_format_>`_ for information how to use new-style Python formatting.

Specify Additional Build Targets
================================

In addition to generating static HTML documentation, it is also possible to specify additional build targets for each version of your documentation by providing a value for the ``smv_build_targets`` setting. This can be used to generate and package the documentation for download, or for post processing by an external program. The ``smv_build_targets`` setting has the following format:

.. code-block:: python

   smv_build_targets = {
       "build_target_name" : {
           "builder": `<class sphinx.builders>`,
           "downloadable": bool,
           "download_format": str
       },
   }

These fields can be populated as follows:

* ``build_target_name``: This is the name of the build target. It must be unique within the ``smv_build_targets`` dictionary, and is used as the display name of the download artefacts if ``downloadable == True``.
* ``builder``: This is the string identifying any valid `sphinx builder <https://www.sphinx-doc.org/en/master/usage/builders/index.html>`_.
* ``downloadable``: Indicate whether an artefact for this build should be generated. All artefacts are placed within the ``build/version/artefacts`` directory and made available in the html context.
* ``download_format``: A string indicating the format of the final downloadable artefact. Only valid if ``downloadable == True``. Valid values for this include ``tar``, ``zip``, ``pdf``, ``epub``, or any other extension for build artefacts produced by the sphinx builder specified in ``builder``.

  .. note::

     If ``tar`` or ``zip`` are specified, the entire build directory is archived. An example of this would be the ``html`` directory for a ``html`` sphinx builder, or the ``latex`` directory for a ``latex`` sphinx builder.

  .. note::

     When the build artefact is an individual file, it is only matched according to the pattern <project>.<download_format> to avoid the ambiguity associated with multiple matches to a file extension. To illustrate this limitation, html files are always indexed with ``index.html``, which would not be identified as an individual build artefact. Thus, in order to make HTML available as a build artefact it must be archived using ``zip``, ``tar``, ``gztar``, ``bztar`` or ``xztar``.

Some common examples may be as follows:

.. code-block:: python

   smv_build_targets = {
       "HTML" : {
           "builder": "html",
           "downloadable": True,
           "download_format": "zip",
       },
       "SingleHTML" : {
           "builder": "singlehtml",
           "downloadable": True,
           "download_format": "tar",
       },
       "PDF" : {
           "builder": "latexpdf", # This will build a .pdf file after generating latex documents
           "downloadable": True,
           "download_format": "pdf",
       },
       "LaTeX" : {
           "builder": "latex", # This will only generate latex documents.
           "downloadable": True,
           "download_format": "gztar",
       },
       "ePub" : {
           "builder": "epub",
           "downloadable": True,
           "download_format": "epub",
       },
   }

Additionally, the user is able to configure whether intermediate build files are cleaned from the output directory using the ``smv_clean_intermediate_files`` setting:

.. code-block:: python

   smv_clean_intermediate_files = True

If this flag is ``True``, the resulting directory structure will resemble the following:

.. code-block:: bash

   build
   ├── develop
   │   ├── artefacts
   │   │   ├── example_docs-develop.epub
   │   │   ├── example_docs-develop-HTML.zip
   │   │   └── example_docs-develop.pdf
   │   ├── index.html
   │   └── ...
   ├── master
   │   ├── artefacts
   │   │   ├── example_docs-master.epub
   │   │   ├── example_docs-master-HTML.zip
   │   │   └── example_docs-master.pdf
   │   ├── index.html
   │   └── ...
   └── v0.1.0
       ├── artefacts
       │   ├── example_docs-v0.1.0.epub
       │   ├── example_docs-v0.1.0-HTML.zip
       │   └── example_docs-v0.1.0.pdf
       ├── index.html
       └── ...

However, if this flag is set to ``False``, the resulting directory will also include intermediate build directories:

.. code-block:: bash

   build
   ├── develop
   │   ├── artefacts
   │   │   ├── example_docs-develop.epub
   │   │   ├── example_docs-develop-HTML.zip
   │   │   └── example_docs-develop.pdf
   │   ├── epub
   │   │   ├── example.epub
   │   │   ├── index.xhtml
   │   │   └── ...
   │   ├── html
   │   │   ├── index.html
   │   │   └── ...
   │   ├── index.html
   │   ├── latexpdf
   │   │   └── latex
   │   └── ...
   ├── master
   │   ├── artefacts
   │   │   ├── example_docs-master.epub
   │   │   ├── example_docs-master-HTML.zip
   │   │   └── example_docs-master.pdf
   │   ├── epub
   │   │   ├── example.epub
   │   │   ├── index.xhtml
   │   │   └── ...
   │   ├── html
   │   │   ├── index.html
   │   │   └── ...
   │   ├── index.html
   │   ├── latexpdf
   │   │   └── latex
   │   └── ...
   └── v0.1.0
       ├── artefacts
       │   ├── example_docs-v0.1.0.epub
       │   ├── example_docs-v0.1.0-HTML.zip
       │   └── example_docs-v0.1.0.pdf
       ├── epub
       │   ├── example.epub
       │   ├── index.xhtml
       │   └── ...
       ├── html
       │   ├── index.html
       │   └── ...
       ├── index.html
       ├── latexpdf
       │   └── latex
       └── ...

This will be useful if you want to use an external program to interact with the build output.


Overriding Configuration Variables
==================================

You can override configuration variables the same way as you're used to with ``sphinx-build``.

Since ``sphinx-multiversion`` copies the branch data into a temporary directory and builds them there while leaving the current working directory unchanged, relative paths in your :file:`conf.py` will refer to the path of the version *you're building from*, not the path of the version you are trying to build documentation for.

Sometimes it might be necessary to override the configured path via a command line overide.
``sphinx-multiversion`` allows you to insert placeholders into your override strings that will automatically be replaced with the correct value for the version you're building the documentation for.

Here's an example for the `exhale extension <exhale_>`_:

.. code-block:: python

    sphinx-multiversion docs build/html -D 'exhale_args.containmentFolder=${sourcedir}/api'

.. note::

    Make sure to enclose the override string in single quotes (``'``) to prevent the shell from treating it as an environment variable and replacing it before it's passed to ``sphinx-multiversion``.

.. note::

    To see a list of available placeholder names and their values for each version you can use the ``--dump-metadata`` flag.

.. _python_regex: https://docs.python.org/3/howto/regex.html
.. _python_format: https://pyformat.info/
.. _exhale: https://exhale.readthedocs.io/en/latest/
