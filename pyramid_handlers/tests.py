import unittest
from pyramid import testing

class Test_add_handler(unittest.TestCase):
    def _makeOne(self):
        from pyramid.config import Configurator
        from pyramid_handlers import add_handler
        config = Configurator(autocommit=True)
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
        from pyramid.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, config.add_handler,
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
        import pyramid
        views = []
        config = self._makeOne()
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_handler('name', '/abc', 'pyramid')
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['view'], pyramid)

    def test_add_handler_pattern_None_no_previous_route(self):
        from pyramid.exceptions import ConfigurationError
        config = self._makeOne()
        self.assertRaises(ConfigurationError, config.add_handler,
                          'name', None, 'pyramid')

    def test_add_handler_pattern_None_with_previous_route(self):
        import pyramid
        config = self._makeOne()
        config.add_route('name', ':def')
        views = []
        def dummy_add_view(**kw):
            views.append(kw)
        config.add_view = dummy_add_view
        config.add_route = None # shouldn't be called
        config.add_handler('name', None, 'pyramid')
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view['view'], pyramid)


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
        self.failUnless(result is wrapped)
        self.assertEqual(result.__exposed__, [{'a':1, 'b':2}])

    def test_call_with_previous__exposed__(self):
        inst = self._makeOne(a=1, b=2)
        def wrapped():
            """ """
        wrapped.__exposed__ = [None]
        result = inst(wrapped)
        self.failUnless(result is wrapped)
        self.assertEqual(result.__exposed__, [None, {'a':1, 'b':2}])

class Test_includeme(unittest.TestCase):
    def test_it(self):
        from pyramid.config import Configurator
        from pyramid_handlers import add_handler
        from pyramid_handlers import includeme
        c = Configurator(autocommit=True)
        c.include(includeme)
        self.failUnless(c.add_handler.im_func is add_handler)

class DummyHandler(object): # pragma: no cover
    def __init__(self, request):
        self.request = request

    def action1(self):
        return 'response 1'

    def action2(self):
        return 'response 2'
