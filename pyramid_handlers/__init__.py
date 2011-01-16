import inspect
import re

from pyramid.exceptions import ConfigurationError

def add_handler(self, route_name, pattern, handler, action=None, **kw):
    """ Add a Pylons-style view handler.  This function adds a
    route and some number of views based on a handler object
    (usually a class).

    This function should never be called directly; instead the
    ``pyramid_handlers.includeme`` function should be included into an
    application and this function will be available as a method of the
    resulting configurator.

    ``route_name`` is the name of the route (to be used later in
    URL generation).

    ``pattern`` is the matching pattern,
    e.g. ``'/blog/{action}'``.  ``pattern`` may be ``None``, in
    which case the pattern of an existing route named the same as
    ``route_name`` is used.  If ``pattern`` is ``None`` and no
    route named ``route_name`` exists, a ``ConfigurationError`` is
    raised.

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

    See :ref:`views_chapter` for more explanatory documentation.

    This method returns the result of add_route."""
    handler = self.maybe_dotted(handler)

    if pattern is not None:
        route = self.add_route(route_name, pattern, **kw)
    else:
        mapper = self.get_routes_mapper()
        route = mapper.get_route(route_name)
        if route is None:
            raise ConfigurationError(
                'The "pattern" parameter may only be "None" when a route '
                'with the route_name argument was previously registered. '
                'No such route named %r exists' % route_name)

        pattern = route.pattern

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

    path_has_action = ':action' in pattern or '{action}' in pattern

    if action and path_has_action:
        raise ConfigurationError(
            'action= (%r) disallowed when an action is in the route '
            'path %r' % (action, pattern))

    if path_has_action:
        autoexpose = getattr(handler, '__autoexpose__', r'[A-Za-z]+')
        if autoexpose:
            try:
                autoexpose = re.compile(autoexpose).match
            except (re.error, TypeError), why:
                raise ConfigurationError(why[0])
        for method_name, method in inspect.getmembers(
            handler, inspect.ismethod):
            configs = getattr(method, '__exposed__', [])
            if autoexpose and not configs:
                if autoexpose(method_name):
                    configs = [{}]
            for expose_config in configs:
                # we don't want to mutate any dict in __exposed__,
                # so we copy each
                view_args = expose_config.copy()
                action = view_args.pop('name', method_name)
                preds = list(view_args.pop('custom_predicates', []))
                preds.append(ActionPredicate(action))
                view_args['custom_predicates'] = preds
                self.add_view(view=handler, attr=method_name,
                              route_name=route_name,
                              decorator=action_decorator, **view_args)
    else:
        method_name = action
        if method_name is None:
            method_name = '__call__'

        # Scan the controller for any other methods with this action name
        for meth_name, method in inspect.getmembers(
            handler, inspect.ismethod):
            configs = getattr(method, '__exposed__', [{}])
            for expose_config in configs:
                # Don't re-register the same view if this method name is
                # the action name
                if meth_name == action:
                    continue
                # We only reg a view if the name matches the action
                if expose_config.get('name') != method_name:
                    continue
                # we don't want to mutate any dict in __exposed__,
                # so we copy each
                view_args = expose_config.copy()
                del view_args['name']
                self.add_view(view=handler, attr=meth_name,
                              route_name=route_name,
                              decorator=action_decorator, **view_args)

        # Now register the method itself
        method = getattr(handler, method_name, None)
        configs = getattr(method, '__exposed__', [{}])
        for expose_config in configs:
            self.add_view(view=handler, attr=action, route_name=route_name,
                          decorator=action_decorator, **expose_config)

    return route


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
    
