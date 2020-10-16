.. _quickstart:

==========
Quickstart
==========

After :ref:`installation <install>`, using ``sphinx-multiversion`` should be fairly straightforward.

To be able to build multiple versions of Sphinx documentation, ``sphinx-multiversion`` acts as wrapper for ``sphinx-build``.
If you're already using Sphinx documentation for your project, you can now use ``sphinx-multiversion`` to build the HTML documentation.
You can check if it works by running:

.. code-block:: bash

    # Without sphinx-multiversion
    sphinx-build docs build/html

    # With sphinx-multiversion
    sphinx-multiversion docs build/html

Don't worry - no version picker will show up in the generated HTML yet.
You need to :ref:`configure <configuration>` the extension first.

.. seealso::

   If you're not using Sphinx yet, have a look at the `tutorial <sphinx_tutorial_>`_.

Next, you need to add the extension to the :file:`conf.py` file.

.. code-block:: python

    extensions = [
        "sphinx_multiversion",
    ]

To make the different versions show up in the HTML, you also need to add a custom template. For example, you could create a new template named :file:`versioning.html` with the following content:

.. code-block:: html

    {% if versions %}
    <h3>{{ _('Versions') }}</h3>
    <ul>
      {%- for item in versions %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    {% endif %}

.. seealso::

   You can also list branches, tags, released versions and development branches separately.
   See :ref:`Templates <templates>` for details.

Assuming that you're using a theme with sidebar widget support, you just need to make sure that the file is inside the ``templates_path`` and add it to the `html_sidebars <sphinx_html_sidebars_>`_ variable.

.. code-block:: python

    templates_path = [
        "_templates",
    ]

    html_sidebars = {
        '**': [
            'versioning.html',
        ],
    }

Now rebuild the documentation:

.. code-block:: bash

    sphinx-multiversion docs build/html

Done!

.. seealso::

   By default, all local branches and tags will be included. If you only want to include certain branches/tags or also include remote branches, see :ref:`Configuration <configuration>`.


.. _sphinx_tutorial: http://www.sphinx-doc.org/en/stable/tutorial.html
.. _sphinx_html_sidebars: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_sidebars
