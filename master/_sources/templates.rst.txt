.. _templates:

=========
Templates
=========

``sphinx-multiversion`` does not change the look of your HTML output by default.
Instead, you can customize the template to cater to your needs.


Version Listings
================

To add version listings to your template, you need to add a custom template to your theme.

You can take one of the snippets below, put it into :file:`_templates/versioning.html` and add it to your theme's sidebar:

.. code-block:: html

    templates_path = [
        "_templates",
    ]

    html_sidebars = [
        "versioning.html",
    ]


List all branches/tags
----------------------

.. code-block:: html

    {% if versions %}
    <h3>{{ _('Versions') }}</h3>
    <ul>
      {%- for item in versions %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    {% endif %}

List branches and tags separately
---------------------------------

.. code-block:: html

    {% if versions %}
    <h3>{{ _('Branches') }}</h3>
    <ul>
      {%- for item in versions.branches %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    <h3>{{ _('Tags') }}</h3>
    <ul>
      {%- for item in versions.tags %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    {% endif %}

List releases and development versions separately
-------------------------------------------------

.. code-block:: html

    {% if versions %}
    <h3>{{ _('Releases') }}</h3>
    <ul>
      {%- for item in versions.releases %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    <h3>{{ _('In Development') }}</h3>
    <ul>
      {%- for item in versions.in_development %}
      <li><a href="{{ item.url }}">{{ item.name }}</a></li>
      {%- endfor %}
    </ul>
    {% endif %}


Version Banners
===============

You can also add version banners to your theme, for example create a template file page.html in the templates directory:

.. code-block:: html

    {% extends "!page.html" %}
    {% block body %}
    {% if current_version and latest_version and current_version != latest_version %}
    <p>
      <strong>
        {% if current_version.is_released %}
        You're reading an old version of this documentation.
        If you want up-to-date information, please have a look at <a href="{{ vpathto(latest_version.name) }}">{{latest_version.name}}</a>.
        {% else %}
        You're reading the documentation for a development version.
        For the latest released version, please have a look at <a href="{{ vpathto(latest_version.name) }}">{{latest_version.name}}</a>.
        {% endif %}
      </strong>
    </p>
    {% endif %}
    {{ super() }}
    {% endblock %}%


ReadTheDocs Theme
=================

As of version 0.4.3, the `Read the Docs theme <sphinx_rtd_theme_>`_ does not support sidebar widgets.
So instead of adding a custom template to ``html_sidebars``, you need to create a template file named :file:`versions.html` with the following content:

.. code-block:: html

    {%- if current_version %}
    <div class="rst-versions" data-toggle="rst-versions" role="note" aria-label="versions">
      <span class="rst-current-version" data-toggle="rst-current-version">
        <span class="fa fa-book"> Other Versions</span>
        v: {{ current_version.name }}
        <span class="fa fa-caret-down"></span>
      </span>
      <div class="rst-other-versions">
        {%- if versions.tags %}
        <dl>
          <dt>Tags</dt>
          {%- for item in versions.tags %}
          <dd><a href="{{ item.url }}">{{ item.name }}</a></dd>
          {%- endfor %}
        </dl>
        {%- endif %}
        {%- if versions.branches %}
        <dl>
          <dt>Branches</dt>
          {%- for item in versions.branches %}
          <dd><a href="{{ item.url }}">{{ item.name }}</a></dd>
          {%- endfor %}
        </dl>
        {%- endif %}
      </div>
    </div>
    {%- endif %}


.. _sphinx_rtd_theme: https://pypi.org/project/sphinx-rtd-theme/
