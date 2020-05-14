class Builder:


    def show(self, a=0):

        def decorator(f):
            print("In Decorator")
            return f

        return decorator



b = Builder()

@b.show(12)
def test():
    print("Hallo")

test()

@b.show()
class Moin:

    def __init__(self):
        print("Class")
