import json
import logging

from digicubes.storage.models import User, Role, Right
from responder.core import Response
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise import transactions

from .util import BasicRessource, error_response, needs_typed_parameter, needs_int_parameter

from .. import Blueprint

logger = logging.getLogger(__name__)


class RightsRessource(BasicRessource):
    async def on_get(self, req, resp):
        filter_fields = self.get_filter_fields(req)
        logger.debug(f"Requesting {filter_fields} fields.")
        rights = [right.to_dict(filter_fields) for right in await Right.all()]
        resp.media = rights

    async def on_post(self, req, resp):
        data = await req.media()
        if isinstance(data, dict):
            # Inserting a single right
            name = data["name"]
            right = await Right.create(name=name)
            resp.media = right.to_dict()
            return

        if isinstance(data, list):
            # Buld insert
            # Bulk insert is wrapped in a transaction
            # If one item violates a constraint, the
            # whole operation will fail.
            transaction = await transactions.start_transaction()
            try:
                new_rights = [Right.from_dict(item) for item in data]
                for right in new_rights:
                    print(right)
                await Right.bulk_create(new_rights)
                await transaction.commit()
                return
            except IntegrityError as e:
                logger.error(f"Creation of {len(new_rights)} new rights failed. Rolling back. {e}")
                await transaction.rollback()
                error_response(resp, 409, str(e))
                return
            except Exception as e:
                logger.error(f"Creation of {len(new_rights)} new rights failed. Rolling back. {e}")
                await transaction.rollback()
                error_response(resp, 500, str(e))
                return

        # Unsupported type
        resp.status_code = 400

    async def on_delete(self, req, resp):
        try:
            await Right.all().delete()
        except Exception as e:
            error_response(resp, 500, str(e))
