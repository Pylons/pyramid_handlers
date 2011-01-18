.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   Pyramid
      A `web framework <http://pylonshq.com/pyramid>`_.

   View handler
     A view handler ties together
     :meth:`pyramid.config.Configurator.add_route` and
     :meth:`pyramid.config.Configurator.add_view` to make it more
     convenient to register a collection of views as a single class when
     using :term:`url dispatch`.  See also :ref:`views_chapter`.

   Pylons
     `A lightweight Python web framework <http://pylonshq.com>`_.

   URL dispatch
     An alternative to :term:`traversal` as a mechanism for locating a a
     :term:`view callable`.  When you use a :term:`route` in your Pyramid
     application via a :term:`route configuration`, you are using URL
     dispatch. See the :ref:`urldispatch_chapter` for more information.

   ZCML
     `Zope Configuration Markup Language
     <http://www.muthukadan.net/docs/zca.html#zcml>`_, an XML dialect
     used by Zope and Pyramid for configuration tasks.  ZCML
     is capable of performing different types of :term:`configuration
     declaration`, but its primary purpose in Pyramid is to
     perform :term:`view configuration` and :term:`route configuration`
     within the ``configure.zcml`` file in a Pyramid
     application.  You can use ZCML as an alternative to
     :term:`imperative configuration`.

   asset specification
     A colon-delimited identifier for an :term:`asset`.  The colon separates
     a Python :term:`package` name from a package subpath.  For example, the
     asset specification ``my.package:static/baz.css`` identifies the file
     named ``baz.css`` in the ``static`` subdirectory of the ``my.package``
     Python :term:`package`.  See :ref:`asset_specifications` for more info.

   view callable
     A "view callable" is a callable Python object which is associated with a
     :term:`view configuration`; it returns a :term:`response` object .  A
     view callable accepts a single argument: ``request``, which will be an
     instance of a :term:`request` object.  A view callable is the primary
     mechanism by which a developer writes user interface code within
     Pyramid.  See :ref:`views_chapter` for more information about Pyramid
     view callables.

   view
     Common vernacular for a :term:`view callable`.

   view predicate
     An argument to a :term:`view configuration` which evaluates to
     ``True`` or ``False`` for a given :term:`request`.  All predicates
     attached to a view configuration must evaluate to true for the
     associated view to be considered as a possible callable for a
     given request.

   traversal
     The act of descending "up" a tree of resource objects from a root
     resource in order to find a context resource.  The Pyramid
     :term:`router` performs traversal of resource objects when a :term:`root
     factory` is specified.  See the :ref:`traversal_chapter` chapter for
     more information.  Traversal can be performed *instead* of :term:`URL
     dispatch` or can be combined *with* URL dispatch.  See
     :ref:`hybrid_chapter` for more information about combining traversal and
     URL dispatch (advanced).

   imperative configuration
     The configuration mode in which you use Python to call methods on
     a :term:`Configurator` in order to add each :term:`configuration
     declaration` required by your application.

   route configuration
     Route configuration is the act of using :term:`imperative
     configuration` or a :term:`ZCML` ``<route>`` statement to
     associate request parameters with a particular :term:`route` using
     pattern matching and :term:`route predicate` statements.  See
     :ref:`urldispatch_chapter` for more information about route
     configuration.

   view configuration
     View configuration is the act of associating a :term:`view callable`
     with configuration information.  This configuration information helps
     map a given :term:`request` to a particular view callable and it can
     influence the response of a view callable.  Pyramid views can be
     configured via :term:`imperative configuration`, :term:`ZCML` or by a
     special ``@view_config`` decorator coupled with a :term:`scan`.  See
     :ref:`view_config_chapter` for more information about view
     configuration.

   configuration declaration
     An individual method call made to an instance of a Pyramid
     :term:`Configurator` object which performs an arbitrary action, such as
     registering a :term:`view configuration` (via the ``add_view`` method of
     the configurator) or :term:`route configuration` (via the ``add_route``
     method of the configurator).

   request
     A ``WebOb`` request object.  See :ref:`webob_chapter` (narrative)
     and :ref:`request_module` (API documentation) for information
     about request objects.

   scan
     The term used by Pyramid to define the process of
     importing and examining all code in a Python package or module for
     :term:`configuration decoration`.

   route
     A single pattern matched by the :term:`url dispatch` subsystem, which
     generally resolves to one or more :term:`view callable` objects.  See
     also :term:`url dispatch`.

   asset
     Any file contained within a Python :term:`package` which is *not*
     a Python source code file.

   asset specification
     A colon-delimited identifier for an :term:`asset`.  The colon separates
     a Python :term:`package` name from a package subpath.  For example, the
     asset specification ``my.package:static/baz.css`` identifies the file
     named ``baz.css`` in the ``static`` subdirectory of the ``my.package``
     Python :term:`package`.  See :ref:`asset_specifications` for more info.

   package
     A directory on disk which contains an ``__init__.py`` file, making
     it recognizable to Python as a location which can be ``import`` -ed.
     A package exists to contain :term:`module` files.

   module
     A Python source file; a file on the filesystem that typically ends with
     the extension ``.py`` or ``.pyc``.  Modules often live in a 
     :term:`package`.

   configurator
     An object used to do :term:`configuration declaration` within an
     application.  The most common configurator is an instance of the
     ``pyramid.config.Configurator`` class.

   route predicate
     An argument to a :term:`route configuration` which implies a value
     that evaluates to ``True`` or ``False`` for a given
     :term:`request`.  All predicates attached to a :term:`route
     configuration` must evaluate to ``True`` for the associated route
     to "match" the current request.  If a route does not match the
     current request, the next route (in definition order) is
     attempted.

   root factory
     The "root factory" of an Pyramid application is called
     on every request sent to the application.  The root factory
     returns the traversal root of an application.  It is
     conventionally named ``get_root``.  An application may supply a
     root factory to Pyramid during the construction of a
     :term:`Configurator`.  If a root factory is not supplied, the
     application uses a default root object.  Use of the default root
     object is useful in application which use :term:`URL dispatch` for
     all URL-to-view code mappings.

   configuration decoration
     Metadata implying one or more :term:`configuration declaration`
     invocations.  Often set by configuration Python :term:`decorator`
     attributes, such as :class:`pyramid.view.view_config`, aka
     ``@view_config``.

   decorator
     A wrapper around a Python function or class which accepts the function
     or class as its first argument and which returns an arbitrary object.
     Pyramid provides several decorators, used for configuration and return
     value modification purposes.  See also `PEP 318
     <http://www.python.org/dev/peps/pep-0318/>`_.

   router
     The :term:`WSGI` application created when you start a
     Pyramid application.  The router intercepts requests,
     invokes traversal and/or URL dispatch, calls view functions, and
     returns responses to the WSGI server on behalf of your
     Pyramid application.

   WSGI
     `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
     Python standard for connecting web applications to web servers,
     similar to the concept of Java Servlets.  Pyramid requires
     that your application be served as a WSGI application.

   dotted Python name
     A reference to a Python object by name using a string, in the form
     ``path.to.modulename:attributename``.  Often used in Paste and
     setuptools configurations.  A variant is used in dotted names within
     configurator method arguments that name objects (such as the "add_view"
     method's "view" and "context" attributes): the colon (``:``) is not
     used; in its place is a dot.

   ZCML directive
     A ZCML "tag" such as ``<view>``, ``<route>``, or ``<handler>``.

   ZCML declaration
     The concrete use of a :term:`ZCML directive` within a ZCML file.

   application registry
     A registry of configuration information consulted by Pyramid while
     servicing an application.  An application registry maps resource types
     to views, as well as housing other application-specific component
     registrations.  Every Pyramid application has one (and only one)
     application registry.
