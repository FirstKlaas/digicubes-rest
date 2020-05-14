from responder import API

class BluePrint(object):

    def __init__(self, prefix=None):
        self._prefix = prefix if prefix else ""
        self._routes = []

    def show(self, a=0):

        def decorator(f):
            print("In Decorator")
            return f

        return decorator

    def register(self, api: API):
        for route, endpoint, options in self._routes:
            api.add_route(f"{self._prefix}{route}", endpoint, **options)

    def __str__(self):
        return f"Blueprint(prefix='{self._prefix}')"

    def __repr__(self):
        return f"Blueprint(prefix='{self._prefix}')"
