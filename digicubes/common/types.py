# pylint: disable=C0111
from typing import Union, Optional, List

from .entities import RightEntity

TRights = Optional[Union[Union[RightEntity, str], List[Union[RightEntity, str]]]]
