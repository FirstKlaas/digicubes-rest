class Meta(type):
    def __init__(cls, name, bases, nmspc):
        print(f"Class: {cls}, name: {name}, bases:{bases}, nmspc:{nmspc}")
        

class Demo(metaclass=Meta):
    pass


class Child(Demo):
    pass



