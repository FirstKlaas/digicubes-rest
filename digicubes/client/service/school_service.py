"""
All service calls for schooles.
"""
from typing import Optional, List

from digicubes.common.exceptions import (
    ConstraintViolation,
    ServerError,
)
from digicubes.configuration import Route
from .abstract_service import AbstractService
from ..proxy import SchoolProxy

SchoolList = Optional[List[SchoolProxy]]


class SchoolService(AbstractService):
    """
    School services
    """

    def all(self) -> SchoolList:
        """
        Returns all schools.
        The result is a list of ``SchoolProxy`` objects.
        """
        headers = self.create_default_header()
        url = self.url_for(Route.schools)
        result = self.requests.get(url, headers=headers)

        if result.status_code == 404:
            return []

        return [SchoolProxy.structure(school) for school in result.json()]

    def create(self, school: SchoolProxy) -> SchoolProxy:
        """
        Create a new school
        """
        headers = self.create_default_header()
        data = school.unstructure()
        url = self.url_for(Route.schools)
        result = self.requests.post(url, json=data, headers=headers)
        if result.status_code == 201:
            return SchoolProxy.structure(result.json())

        if result.status_code == 409:
            raise ConstraintViolation(result.text)

        if result.status_code == 500:
            raise ServerError(result.text)

        raise ServerError(f"Unknown error. [{result.status_code}] {result.text}")

    def create_bulk(self, schools: List[SchoolProxy]) -> None:
        """
        Create multiple schools
        """
        headers = self.create_default_header()
        data = [school.unstructure() for school in schools]
        url = self.url_for(Route.schools)
        result = self.requests.post(url, json=data, headers=headers)

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
        headers = self.create_default_header()
        url = self.url_for(Route.schools)
        result = self.requests.delete(url, headers=headers)
        if result.status_code != 200:
            raise ServerError(result.text)
