import sys
import unittest
from pyramid import testing
from pyramid.config import Configurator

PY3 = sys.version_info[0] == 3

class Test_add_handler(unittest.TestCase):
    def _makeOne(self, autocommit=True):
        from pyramid.config import Configurator
        from pyramid_handlers import add_handler
        config = Configurator(autocommit=autocommit)
        config.add_directive('add_handler', add_handler)
        return config
        
    def test_add_handler_action_in_route_pattern(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/:action', DummyHandler)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 2)

        view = views[0]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'action1'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action1')
        self.assertEqual(view['view'], DummyHandler)

        view = views[1]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'action2'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action2')
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_action_in_route_pattern_with_xformer(self):
        config = self._makeOne()
        def x(name):
            return name.upper()
        config.registry.settings['pyramid_handlers.method_name_xformer'] = x
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/:action', DummyHandler)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 2)

        view = views[0]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'ACTION1'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action1')
        self.assertEqual(view['view'], DummyHandler)

        view = views[1]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'ACTION2'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action2')
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_with_view_overridden_autoexpose_None(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw) # pragma: no cover
        config.add_view = dummy_add_view
        class MyView(DummyHandler):
            __autoexpose__ = None
        config.add_handler('name', '/:action', MyView)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 0)

    def test_add_handler_with_view_overridden_autoexpose_broken_regex1(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        def dummy_add_view(**kw):
            """ """
        config.add_view = dummy_add_view
        class MyView(DummyHandler):
            __autoexpose__ = 1
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', '/{action}', MyView)

    def test_add_handler_with_view_overridden_autoexpose_broken_regex2(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        def dummy_add_view(**kw):
            """ """
        config.add_view = dummy_add_view
        class MyView(DummyHandler):
            __autoexpose__ = 'a\\'
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', '/{action}', MyView)

    def test_add_handler_with_view_method_has_expose_config(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        class MyView(object):
            def action(self): # pragma: no cover
                return 'response'
            action.__exposed__ = [{'custom_predicates':(1,)}]
        config.add_handler('name', '/:action', MyView)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 1)
        view = views[0]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 2)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action')
        self.assertEqual(view['view'], MyView)

    def test_add_handler_with_view_method_has_expose_config_with_action(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        class MyView(object):
            def action(self): # pragma: no cover
                return 'response'
            action.__exposed__ = [{'name':'action3000'}]
        config.add_handler('name', '/:action', MyView)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 1)
        view = views[0]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'action3000'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action')
        self.assertEqual(view['view'], MyView)

    def test_add_handler_with_view_method_has_expose_config_with_action_regex(
        self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        class MyView(object):
            def action(self): # pragma: no cover
                return 'response'
            action.__exposed__ = [{'name':'^action3000$'}]
        config.add_handler('name', '/:action', MyView)
        self._assertRoute(config, 'name', '/:action', 0)
        self.assertEqual(len(views), 1)
        view = views[0]
        preds = view['custom_predicates']
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)
        request.matchdict = {'action':'action3000'}
        self.assertEqual(pred(None, request), True)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['attr'], 'action')
        self.assertEqual(view['view'], MyView)

    def test_add_handler_with_action_decorator(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        class MyHandler(object):
            @classmethod
            def __action_decorator__(cls, fn): # pragma: no cover
                return fn
            def action(self): # pragma: no cover
                return 'response'
        config.add_handler('name', '/{action}', MyHandler)
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0]['decorator'], MyHandler.__action_decorator__)

    def test_add_handler_with_action_decorator_fail_on_instancemethod(self):
        config = self._makeOne()
        class MyHandler(object):
            def __action_decorator__(self, fn): # pragma: no cover
                return fn
            def action(self): # pragma: no cover
                return 'response'
        self.assertRaises(TypeError, config.add_handler,
                          'name', '/{action}', MyHandler)

    def test_add_handler_doesnt_mutate_expose_dict(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        exposed = [{'name':'^action3000$'}]
        class MyView(object):
            def action(self): # pragma: no cover
                return 'response'
            action.__exposed__ = exposed
        config.add_handler('name', '/{action}', MyView)
        self.assertEqual(exposed[0], {'name':'^action3000$'}) # not mutated

    def test_add_handler_with_action_and_action_in_path(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', '/{action}', DummyHandler, action='abc')

    def test_add_handler_with_explicit_action(self):
        config = self._makeOne()
        class DummyHandler(object):
            def index(self): pass
            index.__exposed__ = [{'a':'1'}]
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/abc', DummyHandler, action='index')
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['a'], '1')
        self.assertEqual(view['attr'], 'index')
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_with_implicit_action(self):
        config = self._makeOne()
        class DummyHandler(object):
            def __call__(self): pass
            __call__.__exposed__ = [{'a':'1'}]
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/abc', DummyHandler)
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['a'], '1')
        self.assertEqual(view['attr'], None)
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_with_multiple_action(self):
        config = self._makeOne()
        class DummyHandler(object):
            def index(self): pass
            def create(self): pass
            create.__exposed__ = [{'name': 'index'}]
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/abc', DummyHandler, action='index')
        self.assertEqual(len(views), 2)
        view = views[0]
        self.assertEqual(view['attr'], 'create')
        self.assertEqual(view['route_name'], 'name')
        self.assertEqual(view['view'], DummyHandler)
        view = views[1]
        self.assertEqual(view['attr'], 'index')

    def test_add_handler_string(self):
        views = []
        config = self._makeOne()
        def dummy_add_view(**kw):
            views.append(kw)
        class DummyHandler(object):
            def one(self): pass
        config.add_view = dummy_add_view
        config.add_handler('name', '/abc', DummyHandler)
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_pattern_None_no_previous_route(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', None, 'pyramid')

    def test_add_handler_pattern_None_with_previous_route(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        config.add_route('name', ':def')
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', None, 'pyramid')
    
    def test_add_handler_explicit_action_lacking(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw): views.append(kw)
        class DummyHandler(object):
            def one(self): pass
        config.add_view = dummy_add_view # shouldn't be called
        config.add_handler('name', ':def', DummyHandler, action='two')
        self.assertEqual(len(views), 0)

    def test_add_handler_explicit_action_and_extra_exposed(self):
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw): views.append(kw)
        class DummyHandler(object):
            def two(self): pass
            two.__exposed__ = [{'name':'one'}]
        config.add_view = dummy_add_view # shouldn't be called
        config.add_handler('name', ':def', DummyHandler, action='two')
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['view'], DummyHandler)

    def test_add_handler_with_view_permission_and_action_in_path(self):
        from pyramid_handlers import action
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw) # pragma: no cover
        config.add_view = dummy_add_view
        class MyView(DummyHandler):
            @action(permission='different_perm')
            def action_with_non_default_permission(self): # pragma: no cover
                return 'My permission is different!'
        config.add_handler('name', '/{action}', MyView, view_permission='perm')
        self._assertRoute(config, 'name', '/{action}', 0)
        self.assertEqual(len(views), 3)
        for view in views:
            self.assertTrue('permission' in view)
            if view['attr'] == 'action_with_non_default_permission':
                self.assertEqual(view['permission'], 'different_perm')
            else:
                self.assertEqual(view['permission'], 'perm')

    def test_add_handler_with_view_permission_and_action_as_kwarg(self):
        from pyramid_handlers import action
        config = self._makeOne()
        views = []
        def dummy_add_view(**kw):
            views.append(kw) # pragma: no cover
        config.add_view = dummy_add_view
        class MyView(DummyHandler):
            def index(self): # pragma: no cover
                return 'Index'
            @action(name='index', permission='different_perm')
            def index2(self): # pragma: no cover
                return 'Index with different permission.'
        config.add_handler('name', '/', MyView, action='index',
                           view_permission='perm')
        self._assertRoute(config, 'name', '/', 0)
        self.assertEqual(len(views), 2)
        for view in views:
            self.assertTrue('permission' in view)
            if view['attr'] == 'index':
                self.assertEqual(view['permission'], 'perm')
            elif view['attr'] == 'index2':
                self.assertEqual(view['permission'], 'different_perm')

    def _assertRoute(self, config, name, path, num_predicates=0):
        from pyramid.interfaces import IRoutesMapper
        mapper = config.registry.getUtility(IRoutesMapper)
        routes = mapper.get_routes()
        route = routes[0]
        self.assertEqual(len(routes), 1)
        self.assertEqual(route.name, name)
        self.assertEqual(route.path, path)
        self.assertEqual(len(routes[0].predicates), num_predicates)
        return route

    def test_conflict_add_handler(self):
        class AHandler(object):
            def aview(self): pass
        config = self._makeOne(autocommit=False)
        config.add_handler('h1', '/h1', handler=AHandler)
        config.add_handler('h1', '/h1', handler=AHandler)
        try:
            config.commit()
        except Exception as why:
            c = list(self._conflictFunctions(why))
            self.assertEqual(c[0], 'test_conflict_add_handler')
            self.assertEqual(c[1], 'test_conflict_add_handler')
        else: # pragma: no cover
            raise AssertionError

    def _conflictFunctions(self, e):
        conflicts = e._conflicts.values()
        for conflict in conflicts:
            for confinst in conflict:
                try:
                    # pyramid 1.2 
                    yield confinst[2]
                except TypeError:
                    yield confinst.function

class TestActionPredicate(unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_handlers import ActionPredicate
        return ActionPredicate

    def _makeOne(self, action='myaction'):
        return self._getTargetClass()(action)

    def test_bad_action_regex_string(self):
        from pyramid.exceptions import ConfigurationError
        cls = self._getTargetClass()
        self.assertRaises(ConfigurationError, cls, '[a-z')

    def test_bad_action_regex_None(self):
        from pyramid.exceptions import ConfigurationError
        cls = self._getTargetClass()
        self.assertRaises(ConfigurationError, cls, None)

    def test___call__no_matchdict(self):
        pred = self._makeOne()
        request = testing.DummyRequest()
        self.assertEqual(pred(None, request), False)

    def test___call__no_action_in_matchdict(self):
        pred = self._makeOne()
        request = testing.DummyRequest()
        request.matchdict = {}
        self.assertEqual(pred(None, request), False)

    def test___call__action_does_not_match(self):
        pred = self._makeOne()
        request = testing.DummyRequest()
        request.matchdict = {'action':'notmyaction'}
        self.assertEqual(pred(None, request), False)

    def test___call__action_matches(self):
        pred = self._makeOne()
        request = testing.DummyRequest()
        request.matchdict = {'action':'myaction'}
        self.assertEqual(pred(None, request), True)

    def test___call___matchdict_is_None(self):
        pred = self._makeOne()
        request = testing.DummyRequest()
        request.matchdict = None
        self.assertEqual(pred(None, request), False)

    def test___hash__(self):
        pred1 = self._makeOne()
        pred2 = self._makeOne()
        pred3 = self._makeOne(action='notthesame')
        self.assertEqual(hash(pred1), hash(pred2))
        self.assertNotEqual(hash(pred1), hash(pred3))
        self.assertNotEqual(hash(pred2), hash(pred3))

class Test_action(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid_handlers import action
        return action(**kw)

    def test_call_no_previous__exposed__(self):
        inst = self._makeOne(a=1, b=2)
        def wrapped():
            """ """
        result = inst(wrapped)
        self.assertTrue(result is wrapped)
        self.assertEqual(result.__exposed__, [{'a':1, 'b':2}])

    def test_call_with_previous__exposed__(self):
        inst = self._makeOne(a=1, b=2)
        def wrapped():
            """ """
        wrapped.__exposed__ = [None]
        result = inst(wrapped)
        self.assertTrue(result is wrapped)
        self.assertEqual(result.__exposed__, [None, {'a':1, 'b':2}])

if not PY3:
    class TestHandlerDirective(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp(autocommit=False)
            _ctx = self.config._ctx
            if _ctx is None: # pragma: no cover ; will never be true under 1.2a5+
                self.config._ctx = self.config._make_context()

        def tearDown(self):
            testing.tearDown()

        def _callFUT(self, *arg, **kw):
            from pyramid_handlers.zcml import handler
            return handler(*arg, **kw)

        def test_it(self):
            from pyramid_handlers import action
            from zope.interface import Interface
            from pyramid.interfaces import IView
            from pyramid.interfaces import IViewClassifier
            from pyramid.interfaces import IRouteRequest
            reg = self.config.registry
            context = DummyZCMLContext(self.config)
            class Handler(object): # pragma: no cover
                def __init__(self, request):
                    self.request = request
                action(renderer='json')
                def one(self):
                    return 'OK'
                action(renderer='json')
                def two(self):
                    return 'OK'
            self._callFUT(context, 'name', '/:action', Handler)
            actions = extract_actions(context.actions)
            _execute_actions(actions)
            request_type = reg.getUtility(IRouteRequest, 'name')
            wrapped = reg.adapters.lookup(
                (IViewClassifier, request_type, Interface), IView, name='')
            self.assertTrue(wrapped)

        def test_pattern_is_None(self):
            from pyramid.exceptions import ConfigurationError

            context = self.config._ctx
            class Handler(object):
                pass
            self.assertRaises(ConfigurationError, self._callFUT,
                              context, 'name', None, Handler)


class Test_includeme(unittest.TestCase):
    def test_it(self):
        from pyramid.config import Configurator
        from pyramid_handlers import add_handler
        from pyramid_handlers import includeme
        c = Configurator(autocommit=True)
        c.include(includeme)
        self.assertTrue(c.add_handler.__func__.__docobj__ is add_handler)

class DummyHandler(object): # pragma: no cover
    def __init__(self, request):
        self.request = request

    def action1(self):
        return 'response 1'

    def action2(self):
        return 'response 2'

try:
    from pyramid.config import expand_action
    dict_actions = True
except ImportError: # pragma: no cover
    from zope.configuration.config import expand_action
    dict_actions = False

if dict_actions:
    # pyramid 1.Xsomeversion uses dictionary-based actions; the imprecision
    # of which is because i'm at a sprint and figuring out exactly which
    # version is less important than keeping things moving, sorry.
    def extract_actions(native):
        return native

else:
    # some other version of pyramid uses tuple-based actions
    def extract_actions(native): # pragma: no cover
        L = []
        for action in native:
            (discriminator, callable, args, kw, includepath, info, order
             ) = expand_action(*action)
            d = {}
            d['discriminator'] = discriminator
            d['callable'] = callable
            d['args'] = args
            d['kw'] = kw
            d['order'] = order
            L.append(d)
        return L
    
def _execute_actions(actions):
    try:
        from pyramid.registry import undefer
    except ImportError: # pragma: no cover
        def undefer(discriminator):
            return discriminator
    for action in sorted(actions, key=lambda x: x['order']):
        discriminator = undefer(action['discriminator'])
        action['discriminator'] = discriminator
        if 'callable' in action:
            if action['callable']:
                action['callable']()

class DummyZCMLContext(object):
    config_class = Configurator
    introspection = False
    def __init__(self, config):
        if hasattr(config, '_make_context'): # pragma: no cover
            # 1.0, 1.1 b/c
            config._ctx = config._make_context()
        self.registry = config.registry
        self.package = config.package
        self.autocommit = config.autocommit
        self.route_prefix = getattr(config, 'route_prefix', None)
        self.basepath = getattr(config, 'basepath', None)
        self.includepath = getattr(config, 'includepath', ())
        self.info = getattr(config, 'info', '')
        self.actions = config._ctx.actions
        self._ctx = config._ctx

    def action(self, *arg, **kw): # pragma: no cover
        self._ctx.action(*arg, **kw)
