"""
All service calls for schooles.
"""
from typing import Any, Optional, List

from .abstract_service import AbstractService
from .exceptions import ConstraintViolation, ServerError
from ..proxy import SchoolProxy

SchoolList = Optional[List[SchoolProxy]]


class SchoolService(AbstractService):
    """
    School services
    """

    def __init__(self, client: Any) -> None:
        super().__init__(client, "/schools/")

    def all(self) -> SchoolList:
        """
        Returns all schools.
        The result is a list of ``SchoolProxy`` objects.
        """
        result = self.requests.get(self.path)

        if result.status_code == 404:
            return []

        return [SchoolProxy.structure(school) for school in result.json()]

    def create_bulk(self, schools) -> None:
        """
        Create multiple schools
        """
        data = [school.unstructure() for school in schools]
        result = self.requests.post(self.path, json=data)

        if result.status_code == 201:
            return

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def delete_all(self):
        """
        Deletes all schools from the database. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.
        """
        result = self.requests.delete(self.path)
        if result.status_code != 200:
            raise ServerError(result.text)
