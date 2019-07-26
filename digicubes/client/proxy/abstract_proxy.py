"""
Abstract proxy class

Proxies are pure data containers, that represent orm objects of the server.
Proxies van be converted to json representation as well as created from
a json representation.

The ``AbstractProxy`` just defines the two methos for serialization
and deserialization.
"""
from typing import Any, Dict, List, Optional

import cattr

THeader = Dict[str, str]
TFields = Optional[List[str]]
TStructuredData = Dict[str, Any]


class AbstractProxy:
    """
    An abstract proxy class
    """

    @staticmethod
    def set_filter_fields_header(
        headers: Optional[THeader] = None, fields: TFields = None  # pylint: disable=C0330
    ) -> THeader:
        """
        Set the X-Filter-Fields header. If fields is None, no header is set.
        """
        if headers is None:
            raise ValueError("No header provided")

        if fields is not None:
            headers["X-Filter-Fields"] = ",".join(fields)

        return headers

    @classmethod
    def structure(cls, data: TStructuredData) -> Any:
        """
        This class method creates an instance of this class
        based on the provided data. The data object must
        have at least the attributes defined by the class.
        """
        return cattr.structure(data, cls)

    def unstructure(self, exclude_nones: bool = True) -> TStructuredData:
        """
        Creates a json representation of this instance.

        If the parameter ``exclude_nones`` is ``True``,
        attributes that have a ``None`` value are omitted.

        The default is ``True``.

        :param exclude_nones bool:
            Should atttributes with None value be excluded
            from the result?

        """
        if not exclude_nones:
            return cattr.unstructure(self)

        return {k: v for k, v in cattr.unstructure(self).items() if v is not None}
