class needs_typed_parameter:

    def __init__(self, name, parameter_type):
        self.name = name
        self.parameter_type = parameter_type

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            if self.name not in kwargs:
                raise ValueError(f"Parameter {self.name} not present in named parameters. Got {list(kwargs.keys())}")
            try:
                v = self.parameter_type(kwargs[self.name])
                kwargs[self.name] = v

            except ValueError:
                raise ValueError(f"Expected parameter {self.name} to be of type {self.parameter_type.__name__}")

            return f(*args, **kwargs)
        return wrapped_f

class needs_int_parameter(needs_typed_parameter):

    def __init__(self, name):
        super().__init__(name, type(0))

@needs_int_parameter('test')
def test(*args, **kwargs):
    if 'test' in kwargs:
        print(kwargs['test'])
    else:
        print("No such parameter")


test(test=17)
test(test="hjhsjdh")