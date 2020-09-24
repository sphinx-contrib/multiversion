.. _context:

============
HTML Context
============

The following variables and functions are exposed to the `Sphinx HTML builder context <sphinx_context_>`_ in all versions.

``Version`` Objects
===================

All versions will be exposed to the HTML context as ``Version`` objects with the following attributes:

.. attribute:: name

    The branch or tag name.

.. attribute:: url

    The URL to the current page in this version.

.. attribute:: version

    The value of the ``version`` variable in ``conf.py``.

.. attribute:: release

    The value of the ``release`` variable in ``conf.py``.

.. attribute:: is_released

    ``True`` if this version matches the :ref:`configured <configuration>` ``smv_released_pattern`` regular expression, else ``False``.


Versions
========

The most important variable is ``versions``, which can be used to iterate over all found (and whitelisted) versions.

.. attribute:: versions

    An iterable that yields all ``Version`` objects.

    .. code-block:: jinja

        <h3>Versions</h3>
        <ul>
          {%- for item in versions %}
          <li><a href="{{ item.url }}">{{ item.name }}</a></li>
          {%- endfor %}
        </ul>

.. attribute:: versions.branches

    You can use the ``branches`` property of the ``versions`` iterable to get the ``Version`` objects for all branches.

    .. code-block:: jinja

        <h3>Branches</h3>
        <ul>
          {%- for item in versions.branches %}
          <li><a href="{{ item.url }}">{{ item.name }}</a></li>
          {%- endfor %}
        </ul>

.. attribute:: versions.tags

    You can use the ``tags`` property of the ``versions`` iterable to get the ``Version`` objects for all tags.

    .. code-block:: jinja

        <h3>Tags</h3>
        <ul>
          {%- for item in versions.tags %}
          <li><a href="{{ item.url }}">{{ item.name }}</a></li>
          {%- endfor %}
        </ul>

.. attribute:: versions.releases

    You can use the ``releases`` property of the ``versions`` iterable to get all ``Version`` objects where the ``ìs_released`` attribute is ``True``.
    This is determined by the ``smv_released_pattern`` in the :ref:`Configuration <configuration>`.

    .. code-block:: jinja

        <h3>Releases</h3>
        <ul>
          {%- for item in versions.releases %}
          <li><a href="{{ item.url }}">{{ item.name }}</a></li>
          {%- endfor %}
        </ul>

.. attribute:: versions.in_development

    You can use the ``in_development`` property of the ``versions`` iterable to get all ``Version`` objects where the ``ìs_released`` attribute is ``False``.
    This is determined by the ``smv_released_pattern`` in the :ref:`Configuration <configuration>`.

    .. code-block:: jinja

        <h3>In Development</h3>
        <ul>
          {%- for item in versions.in_development %}
          <li><a href="{{ item.url }}">{{ item.name }}</a></li>
          {%- endfor %}
        </ul>

Functions
=========

Similar to Sphinx's `hasdoc() <sphinx_hasdoc_>`_ function.

.. function:: vhasdoc(other_version)

    This function is Similar to Sphinx's `hasdoc() <sphinx_hasdoc_>`_ function.
    It takes ``other_version`` as string and returns ``True`` if the current document exists in another version.

    .. code-block:: jinja

        {% if vhasdoc('master') %}
        This page is available in <a href="../master/index.html">master</a>.
        {% endif %}

.. function:: vpathto(other_version)

    This function is Similar to Sphinx's `pathto() <sphinx_pathto_>`_ function.
    It takes ``other_version`` as string and returns the relative URL to the current page in the other version.
    If the current page does not exist in that version, the relative URL to its `master_doc <sphinx_master_doc_>`_ is returned instead.

    .. code-block:: jinja

        {% if vhasdoc('master') %}
        This page is also available in <a href="{{ vpathto('master') }}">master</a>.
        {% else %}
        Go to <a href="{{ vpathto('master') }}">master</a> for the latest docs.
        {% endif %}

Other Variables
===============

.. attribute:: current_version

    A ``Version`` object for of the current version being built.

    .. code-block:: jinja

        <h3>Current Version: {{ current_version.name }}</h3>

.. attribute:: latest_version

    A ``Version`` object of the latest released version being built.

    .. code-block:: jinja

        <h3>Latest Version: {{ latest_version.name }}</h3>


.. _sphinx_context: http://www.sphinx-doc.org/en/stable/config.html?highlight=context#confval-html_context
.. _sphinx_master_doc: http://www.sphinx-doc.org/en/stable/config.html?highlight=context#confval-master_doc
.. _sphinx_hasdoc: http://www.sphinx-doc.org/en/stable/templating.html#hasdoc
.. _sphinx_pathto: http://www.sphinx-doc.org/en/stable/templating.html#pathto
