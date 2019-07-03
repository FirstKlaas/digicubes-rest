import responder 

class Blueprint():

    __slots__ = ['prefix', 'routes', 'server']

    def __init__(self, prefix: str):
        self.prefix = prefix[:-1] if prefix.endswith('/') else prefix 
        self.routes = {}
        self.server = None


    def route(self, route, **options):

        def decorator(f):
            _route = route if route.startswith('/') else f"/{route}"
            if _route in self.routes:
                raise ValueError()

            options['endpoint'] = f
            self.routes[_route] = options
            return f

        return decorator

    def register(self, server):
        if self.server is not None:
            return

        assert(isinstance(server, responder.API))
        self.server = server
        for route, args in self.routes.items():
            self.server.add_route(
                route=f"{self.prefix}{route}",
                endpoint=args['endpoint'],
                default=args.get('default', False),
                static=args.get('static', False))    
