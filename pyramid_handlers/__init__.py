import inspect
import re

from pyramid.exceptions import ConfigurationError

action_re = re.compile(r'''({action}|:action)''')

def add_handler(self, route_name, pattern, handler, action=None, **kw):
    """ Add a Pylons-style view handler.  This function adds a
    route and some number of views based on a handler object
    (usually a class).

    This function should never be called directly; instead the
    ``pyramid_handlers.includeme`` function should be used to include this
    function into an application; the function will thereafter be available
    as a method of the resulting configurator.

    ``route_name`` is the name of the route (to be used later in
    URL generation).

    ``pattern`` is the matching pattern, e.g. ``'/blog/{action}'``.

    ``handler`` is a dotted name of (or direct reference to) a
    Python handler class,
    e.g. ``'my.package.handlers.MyHandler'``.

    If ``{action}`` or ``:action`` is in
    the pattern, the exposed methods of the handler will be used
    as views.

    If ``action`` is passed, it will be considered the method name
    of the handler to use as a view.

    Passing both ``action`` and having an ``{action}`` in the
    route pattern is disallowed.

    Any extra keyword arguments are passed along to ``add_route``.

    See :ref:`views_chapter` for more explanatory documentation."""
    if pattern is None:
        raise ConfigurationError('As of version 0.3 pattern cannot be None')

    default_view_args = {
        'permission': kw.pop('view_permission', kw.pop('permission', None))
    }

    self.add_route(route_name, pattern, **kw)

    handler = self.maybe_dotted(handler)
    action_decorator = getattr(handler, '__action_decorator__', None)
    if action_decorator is not None:
        if hasattr(action_decorator, 'im_self'):
            # instance methods have an im_self == None
            # classmethods have an im_self == cls
            # staticmethods have no im_self
            # instances have no im_self
            if action_decorator.im_self is not handler:
                raise ConfigurationError(
                    'The "__action_decorator__" attribute of a handler '
                    'must not be an instance method (must be a '
                    'staticmethod, classmethod, function, or an instance '
                    'which is a callable')

    action_pattern = action_re.search(pattern)
    if action and action_pattern:
        raise ConfigurationError(
            'action= (%r) disallowed when an action is in the route '
            'path %r' % (action, pattern))

    if action_pattern:
        scan_handler(self, handler, route_name, action_decorator,
                     **default_view_args)
    else:
        locate_view_by_name(
            config=self,
            handler=handler,
            route_name=route_name,
            action_decorator=action_decorator,
            name=action,
            **default_view_args
        )


def scan_handler(config, handler, route_name, action_decorator,
                 **default_view_args):
    """Scan a handler for automatically exposed views to register"""
    xformer = config.registry.settings.get(
        'pyramid_handlers.method_name_xformer')
    xformer = config.maybe_dotted(xformer)
    autoexpose = getattr(handler, '__autoexpose__', r'[A-Za-z]+')
    if autoexpose:
        try:
            autoexpose = re.compile(autoexpose).match
        except (re.error, TypeError), why:
            raise ConfigurationError(why[0])
    for method_name, method in inspect.getmembers(handler, inspect.ismethod):
        configs = getattr(method, '__exposed__', [])
        if autoexpose and not configs:
            if autoexpose(method_name):
                configs = [{}]
        for expose_config in configs:
            # we don't want to mutate any dict in __exposed__,
            # so we copy each
            view_args = default_view_args.copy()
            view_args.update(expose_config.copy())
            action = view_args.pop('name', None)
            if action is None:
                action = method_name
                if xformer is not None:
                    action = xformer(action)
            preds = list(view_args.pop('custom_predicates', []))
            preds.append(ActionPredicate(action))
            view_args['custom_predicates'] = preds
            config.add_view(view=handler, attr=method_name,
                            route_name=route_name,
                            decorator=action_decorator, **view_args)


def locate_view_by_name(config, handler, route_name, action_decorator, name,
                        **default_view_args):
    """Locate and add all the views in a handler with the matching name, or
    the method itself if it exists."""
    method_name = name
    if method_name is None:
        method_name = '__call__'

    # Scan the controller for any other methods with this action name
    for attr, method in inspect.getmembers(handler, inspect.ismethod):
        configs = getattr(method, '__exposed__', [{}])
        for expose_config in configs:
            # Don't re-register the same view if this method name is
            # the action name
            if attr == name:
                continue
            # We only reg a view if the name matches the action
            if expose_config.get('name') != method_name:
                continue
            # we don't want to mutate any dict in __exposed__,
            # so we copy each
            view_args = default_view_args.copy()
            view_args.update(expose_config.copy())
            del view_args['name']
            config.add_view(view=handler, attr=attr,
                            route_name=route_name,
                            decorator=action_decorator, **view_args)

    # Now register the method itself
    method = getattr(handler, method_name, None)
    if method:
        configs = getattr(method, '__exposed__', [])
        view_regged = False
        for expose_config in configs:
            if 'name' in expose_config and expose_config['name'] != name:
                continue
            view_regged = True
            view_args = default_view_args.copy()
            view_args.update(expose_config.copy())
            config.add_view(view=handler, attr=name, route_name=route_name,
                            decorator=action_decorator, **view_args)
        if not view_regged:
            config.add_view(view=handler, attr=name, route_name=route_name,
                            decorator=action_decorator, **default_view_args)


class ActionPredicate(object):
    action_name = 'action'
    def __init__(self, action):
        self.action = action
        try:
            self.action_re = re.compile(action + '$')
        except (re.error, TypeError), why:
            raise ConfigurationError(why[0])

    def __call__(self, context, request):
        matchdict = request.matchdict
        if matchdict is None:
            return False
        action = matchdict.get(self.action_name)
        if action is None:
            return False
        return bool(self.action_re.match(action))

    def __hash__(self):
        # allow this predicate's phash to be compared as equal to
        # others that share the same action name
        return hash(self.action)


class action(object):
    """Decorate a method for registration by 
    :func:`~pyramid_handlers.add_handler`.
    
    Keyword arguments are identical to :class:`~pyramid.view.view_config`, with
    the exception to how the ``name`` argument is used.
    
    ``name``
        Designate an alternate action name, rather than the default behavior
        of registering a view with the action name being set to the methods
        name.
    
    """
    def __init__(self, **kw):
        self.kw = kw

    def __call__(self, wrapped):
        if hasattr(wrapped, '__exposed__'):
            wrapped.__exposed__.append(self.kw)
        else:
            wrapped.__exposed__ = [self.kw]
        return wrapped

def includeme(config):
    config.add_directive('add_handler', add_handler)
    
