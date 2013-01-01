pyramid_handlers
================

Overview
--------

``pyramid_handlers`` is a package which allows Pyramid to largely emulate the
functionality of :term:`Pylons` "controllers".  Handlers are a synthesis of
Pyramid *url dispatch* and method introspection of a view class that makes it
easier to create bundles of view logic which reacts to particular route
patterns.

``pyramid_handlers`` works under Python 2.6 and 2.7.  It also works under
Python 3.2, but :term:`ZCML` support is not available under Python 3.2.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_handlers

Setup
-----

Once ``pyramid_handlers`` is installed, you must use the ``config.include``
mechanism to include it into your Pyramid project's configuration.  In your
Pyramid project's ``__init__.py``:

.. code-block:: python
   :linenos:

   config = Configurator(.....)
   config.include('pyramid_handlers')

At this point, it will be possible to use the
:func:`pyramid_handlers.add_handler` function as a method of the
configurator, ala:

.. code-block:: python
   :linenos:

   config.add_handler(....)

.. _using_add_handler:

Handler Registration Using :func:`~pyramid_handlers.add_handler`
----------------------------------------------------------------

``pyramid_handlers`` provides the special concept of a :term:`view handler`.
View handlers are view classes that implement a number of methods, each of
which is a :term:`view callable` as a convenience for :term:`URL dispatch`
users.

.. note:: 

   View handlers are *not* useful when using :term:`traversal`, only when using
   :term:`url dispatch`.  

Using a view handler instead of a plain function or class :term:`view
callable` makes it unnecessary to call
:meth:`pyramid.config.Configurator.add_route` (and/or
:meth:`pyramid.config.Configurator.add_view`) "by hand" multiple times,
making it more pleasant to register a collection of views as a single class
when using :term:`url dispatch`.  The view handler machinery also introduces
the concept of an ``action``, which is used as a :term:`view predicate` to
control which method of the handler is called.  The method name is the
default *action name* of a handler view callable.

The concept of a view handler is analogous to a "controller" in Pylons 1.0.

The view handler class is initialized by Pyramid in the same manner as a
"plain" view class.  Its ``__init__`` is called with a request object (see
:ref:`class_as_view`).  It implements methods, each of which is a :term:`view
callable`.  When a request enters the system which corresponds with an
*action* related to one of its view callable methods, this method is called,
and it is expected to return a response.

Here's an example view handler class:

.. code-block:: python
    :linenos:
    
    from pyramid_handlers import action
   
    from pyramid.response import Response
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
       
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

The :class:`pyramid_handlers.action` decorator is used to fine-tune the view
parameters for each potential view callable which is a method of the handler.

Handlers are added to application configuration via the
:func:`pyramid_handlers.add_handler` API, which is accessible after
configuration as the method ``pyramid.config.Configurator.add_handler``.
This function will scan a :term:`view handler` class and automatically set up
view configurations for its methods that represent "auto-exposed" view
callable, or those that were decorated explicitly with the
:class:`~pyramid_handlers.action` decorator. This decorator is used to setup
additional view configuration information for individual methods of the
class, and can be used repeatedly for a single view method to register
multiple view configurations for it.

.. code-block:: python
    :linenos:

    from myapp.handlers import Hello
    config.add_handler('hello', '/hello/{action}', handler=Hello)

This example will result in a route being added for the pattern
``/hello/{action}``, and each method of the ``Hello`` class will then be
examined to see if it should be registered as a potential view callable when
the ``/hello/{action}`` pattern matches.  The value of ``{action}`` in the
route pattern will be used to determine which view should be called, and each
view in the class will be setup with a view predicate that requires a
specific ``action`` name.  By default, the action name for a method of a
handler is the method name.

If the URL was ``/hello/index``, the above example pattern would match, and,
by default, the ``index`` method of the ``Hello`` class would be called.

Alternatively, the action can be declared specifically for a URL to be
registered for a *specific* ``action`` name:

.. code-block:: python
    :linenos:
    
    from myapp.handlers import Hello
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')

This will result one of the methods that are configured for the ``action`` of
'index' in the ``Hello`` handler class to be called. In this case the name of
the method is the same as  the action name: ``index``. However, this need not
be the case, as we will see below.

When calling :func:`pyramid_handlers.add_handler`, an ``action`` is required
in either the route pattern or as a keyword argument, but **cannot appear in
both places**. A ``handler`` argument must also be supplied, which can be
either a :term:`asset specification` or a Python reference to the handler
class. Additional keyword arguments are passed directly through to
:meth:`pyramid.config.Configurator.add_route`.

For example:

.. code-block:: python
    :linenos:
    
    config.add_handler('hello', '/hello/{action}',
                       handler='mypackage.handlers.MyHandler')

Multiple :meth:`~pyramid.config.Configurator.add_handler` calls can specify
the same handler, to register specific route names for different
handler/action combinations. For example:

.. code-block:: python
    :linenos:
    
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')
    config.add_handler('bye_index', '/hello/bye', 
                       handler=Hello, action='bye')

.. note::

  Handler configuration may also be added to the system via :term:`ZCML` (see
  :ref:`zcml_handler_configuration`).

View Setup in the Handler Class
-------------------------------

A handler class can have a single class level attribute called
``__autoexpose__`` which should be a regular expression or the value
``None``. It's used to determine which method names will result in additional
view configurations being registered.

When :func:`pyramid_handlers.add_handler` runs, every method in the handler
class will be searched and a view registered if the method name matches the
``__autoexpose__`` regular expression, or if the method was decorated with
:class:`~pyramid_handlers.action`.

Every method in the handler class that has a name meeting the
``__autoexpose__`` regular expression will have a view registered for an
``action`` name corresponding to the method name. This functionality can be
disabled by setting the ``__autoexpose__`` attribute to ``None``:

.. code-block:: python
    :linenos:

    from pyramid_handlers import action
   
    class Hello(object):
        __autoexpose__ = None
        
        def __init__(self, request):
            self.request = request
        
        @action()
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

With auto-expose effectively disabled, no views will be registered for a
method unless it is specifically decorated with
:class:`~pyramid_handlers.action`.

Action Decorators in a Handler
++++++++++++++++++++++++++++++

The :class:`~pyramid_handlers.action` decorator registers view configuration
information on the handler method, which is used by
:func:`~pyramid_handlers.add_handler` to setup the view configuration.

All keyword arguments are recorded, and passed to
:meth:`~pyramid.config.Configurator.add_view`. Any valid keyword arguments
for :meth:`~pyramid.config.Configurator.add_view` can thus be used with the
:class:`~pyramid_handlers.action` decorator to further restrict when the view
will be called.

One important difference is that a handler method can respond to an
``action`` name that is different from the method name by passing in a
``name`` argument.

Example:

.. code-block:: python
    :linenos:
    
    from pyramid_handlers import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='index', renderer='created.mak', request_method='POST')
        def create(self):
            return {}

        @action(renderer="view_all.mak", request_method='GET')
        def index(self):
            return {}

This will register two views that require the ``action`` to be ``index``,
with the additional view predicate requiring a specific request method.

It can be useful to decorate a single method multiple times with
:class:`~pyramid_handlers.action`. Each action decorator will register a new
view for the method. By specifying different names and renderers for each
action, the same view logic can be exposed and rendered differently on
multiple URLs.

Example:

.. code-block:: python
    :linenos:
    
    from pyramid_handlers import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='home', renderer='home.mak')
        @action(name='about', renderer='about.mak')
        def show_template(self):
            # prep some template vars
            return {}

    # in the config
    config.add_handler('hello', '/hello/{action}', handler=Hello)

With this configuration, the url ``/hello/home`` will find a view
configuration that results in calling the ``show_template`` method, then
rendering the template with ``home.mak``, and the url ``/hello/about`` will
call the same method and render the ``about.mak`` template.

Handler ``__action_decorator__`` Attribute
------------------------------------------

.. note::

   In a Pylons 1.0 controller, it was possible to override the ``__call__()``
   method, which allowed a developer to "wrap" the entire action invocation,
   with a try/except or any other arbitrary code.  In Pyramid, this
   can be emulated with the use of an ``__action_decorator__`` classmethod
   on your handler class.

If a handler class has an ``__action_decorator__`` attribute, then the
value of the class attribute will be passed in as the ``decorator``
argument every time a handler action is registered as a view callable.
This means that, like anything passed to ``add_view()`` as the
``decorator`` argument, ``__action_decorator__`` must be a callable
accepting a single argument.  This argument will itself be a callable
accepting ``(context, request)`` arguments, and
``__action_decorator__`` must return a replacement callable with the
same call signature.

Note that, since handler actions are registered as views against the
handler class and not a handler instance, any ``__action_decorator__``
attribute must *not* be a regular instance method.  Defining an
``__action_decorator__`` instance method on a handler class will
result in a :exc:`ConfigurationError`.  Instead, ``__action_decorator__``
can be any other type of callable: a staticmethod, classmethod, function,
or some sort of callable instance.

The below example uses an ``__action_decorator__`` which is a staticmethod of
the handler class.  It wraps every view callable implied by the handler in a
decorator function which calls the original view callable, but catches a
special exception and returns a response.

.. code-block:: python
   :linenos:

   from pyramid_handlers import action
   from pyramid.response import Response

   class MySpecialException(Exception):
       pass

   class MyHandler(object):
       def __init__(self, request):
           self.request = request

       @staticmethod
       def __action_decorator__(view):
           def decorated_view(context, request):
               try:
                   return view(context, request)
               except MySpecialException:
                   return Response('Something bad happened', status=500)
           return decorated_view

       @action(renderer='index.html')
       def index(self):
           raise MySpecialException

When the ``index`` method of the above example handler is invoked, it will
raise ``MySpecialException``.  As a result, the action decorator will cath
this exception and turn it into a response.

Configuration Knobs
-------------------

If your handler action methods that have characters in them (such as
underscores) that you don't find appropriate in a URL, such as
``a_method_with_underscores``:

.. code-block:: python
   :linenos:

   # in a module named mypackage.handlers

   from pyramid_handlers import action

   class AHandler(object):
       def __init__(self, request):
           self.request = request

       @action(renderer='some/renderer.pt')
       def a_method_with_underscores(self):
           return {}

And there is some regular transform you can perform against all action method
registrations (such as converting the underscores to dashes), you can define
a "method name transformer":

.. code-block:: python
   :linenos:

   # in the same module named mypackage.handlers

   def transformer(method_name):
       return method_name.replace('_', '-')

You can then use the method name transformer in your Pyramid ``settings`` via
the `.ini`` file:

.. code-block:: ini
   :linenos:

   [app:myapp]
   ...
   pyramid_handlers.method_name_xformer = mypackage.handlers.transformer

Or directly in your ``main()`` function:

.. code-block:: python
   :linenos:

   # in a module named mypackage.handlers

   from mypackage.handlers import transformer

   def main(global_conf, *settings):
       settings['pyramid_handlers.method_name_xformer'] = transformer
       config = Configurator(settings=settings)
       # .. rest of configuration ...

Once you've set up a method name transformer, any ``{action}`` substitution
in the pattern associated with a handler will be matched against the
transformed method name value instead of the untransformed method name value:

.. code-block:: python
   :linenos:

   # in a module named mypackage.handlers

   from mypackage.handlers import transformer
   from mypackage.handlers import AHandler

   def main(global_conf, *settings):
       settings['pyramid_handlers.method_name_xformer'] = transformer
       config = Configurator(settings=settings)
       config.add_handler('ahandler', '/ahandler/{action}', handler=AHandler)
       # .. rest of configuration ...

Now, when ``/ahandler/a-method-with-underscores`` is visited, it will invoke
the ``AHandler.a_method_with_underscores`` method.  Note that
``/ahandler/a_method_with_underscores`` will however no longer work to invoke
the method.


More Information
----------------

.. toctree::
   :maxdepth: 1

   api.rst
   zcml.rst
   glossary.rst


Reporting Bugs / Development Versions
-------------------------------------

Visit http://github.com/Pylons/pyramid_handlers to download development or
tagged versions.

Visit http://github.com/Pylons/pyramid_handlers/issues to report bugs.

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
