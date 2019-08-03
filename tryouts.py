# pyling: disable=C0111
from collections import OrderedDict

d = OrderedDict()

d[1] = 'A'
d[3] = 'C'
d[2] = 'B'

print(d)

d.move_to_end(3)

print(d)
