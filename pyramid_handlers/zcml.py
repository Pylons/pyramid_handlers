from pyramid_zcml import IRouteLikeDirective

from zope.schema import TextLine
from zope.configuration.fields import GlobalObject

from pyramid.exceptions import ConfigurationError

from pyramid.config import Configurator

from pyramid_handlers import add_handler

class IHandlerDirective(IRouteLikeDirective):
    route_name = TextLine(title=u'route_name', required=True)
    handler = GlobalObject(title=u'handler', required=True)
    action = TextLine(title=u"action", required=False)

def handler(_context,
            route_name,
            pattern,
            handler,
            action=None,
            view=None,
            view_for=None,
            permission=None,
            factory=None,
            for_=None,
            header=None,
            xhr=False,
            accept=None,
            path_info=None,
            request_method=None,
            request_param=None,
            custom_predicates=(),
            view_permission=None,
            view_attr=None,
            renderer=None,
            view_renderer=None,
            view_context=None,
            traverse=None,
            use_global_views=False):
    """ Handle ``handler`` ZCML directives
    """
    # the strange ordering of the request kw args above is for b/w
    # compatibility purposes.

    # these are route predicates; if they do not match, the next route
    # in the routelist will be tried
    if view_context is None:
        view_context = view_for or for_

    view_permission = view_permission or permission
    view_renderer = view_renderer or renderer

    if pattern is None:
        raise ConfigurationError('handler directive must include a "pattern"')

    config = Configurator.with_context(_context)
    if not hasattr(config, 'add_handler'):
        config.add_directive('add_handler', add_handler)
    
    config.add_handler(
        route_name,
        pattern,
        handler,
        action=action,
        factory=factory,
        header=header,
        xhr=xhr,
        accept=accept,
        path_info=path_info,
        request_method=request_method,
        request_param=request_param,
        custom_predicates=custom_predicates,
        view=view,
        view_context=view_context,
        view_permission=view_permission,
        view_renderer=view_renderer,
        view_attr=view_attr,
        use_global_views=use_global_views,
        traverse=traverse,
        )


