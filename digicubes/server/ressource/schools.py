# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise import transactions
from tortoise.exceptions import IntegrityError

from digicubes.storage.models import School
from .util import BasicRessource, error_response

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class SchoolsRessource(BasicRessource):
    async def on_get(self, req: Request, resp: Response):
        filter_fields = self.get_filter_fields(req)
        logger.debug("Requesting %s fields.", filter_fields)
        schools = [school.unstructure(filter_fields) for school in await School.all()]
        resp.media = schools

    async def on_post(self, req: Request, resp: Response):
        """
        Create a new school
        """
        logger.debug("POST /schools/")
        data = await req.media()
        if isinstance(data, dict):
            try:
                name = data.get("name", None)
                if name is None:
                    error_response(resp, 400, "Name attribute is missing.")
                else:
                    school = await School.create(name=name)

                    resp.media = school.unstructure()
                    resp.status_code = 201

            except IntegrityError as error:
                error_response(resp, 400, str(error))
            except Exception as error:  # pylint: disable=W0703
                error_response(resp, 500, str(error))

        elif isinstance(data, list):
            # Bulk creation of schools
            transaction = await transactions.start_transaction()
            try:
                new_schools = [School.structure(school) for school in data]
                await School.bulk_create(new_schools)
                await transaction.commit()
                resp.status_code = 201
                return
            except IntegrityError as error:
                logger.error("Can not create multiple schools. %s", error)
                await transaction.rollback()
                error_response(resp, 409, str(error))
                return
            except Exception as error:  # pylint: disable=W0703
                logger.error(
                    "Creation of %s new schools failed. Rolling back. %s", len(new_schools), error
                )
                await transaction.rollback()
                error_response(resp, 400, str(error))
                return
        else:
            error_response(
                resp,
                500,
                f"Unsupported data type {type(data)}"
            )

    async def on_delete(self, req: Request, resp: Response):
        await School.all().delete()
