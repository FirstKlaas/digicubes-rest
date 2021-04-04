from typing import List

from pydantic import BaseModel

class Item(BaseModel):
    nr:int
    n2:int


class ItemList(BaseModel):
    __root__:List[Item]


items = ItemList(__root__=[Item(nr=x, n2=x*2) for x in range(12)])
print(items)
print(items.json(exclude={"n2"}, include=None))
