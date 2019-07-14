# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import IntegrityError
from tortoise import transactions

from digicubes.storage.models import User
from .util import BasicRessource, error_response

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class UsersRoute(BasicRessource):
    """
    GET    : Request all users
    POST   : Create new user
    PUT    : Not implemented
    PATCH  : Not implemented
    DELETE : Forbidden (405)

    Links for the ressources are generated. To avoid the generation
    of links, add an header field 'x-hateoa' with value 'false',
    """

    async def on_get(self, req: Request, resp: Response):
        """
        Requesting all users.
        if the header field 'X-HATEOAS' is available, hyperlinks for
        the ressources in the respond will be generated.

        Possible values for the header field:

        self: only the link to get the ressouce will be generated
        """
        filter_fields = self.get_filter_fields(req)
        users = [user.unstructure(filter_fields) for user in await User.all()]
        resp.media = users

    async def on_post(self, req: Request, resp: Response):
        """
        Create a new user
        """
        data = await req.media()
        logger.info("Requested url is: %s", req.url)
        if isinstance(data, dict):
            #
            # Try to insert a single user ressource
            #
            login = data.get("login", None)
            try:
                user = await User.create(
                    login=login,
                    email=data.get("email", None),
                    firstName=data.get("firstName", None),
                    lastName=data.get("lastName", None),
                )

                resp.media = user.unstructure()
                resp.status_code = 201
            except IntegrityError:
                error_response(
                    resp, 409, f"User with login {login} already exists. Login must be unique."
                )
            except Exception as error:  # pylint: disable=W0703
                error_response(resp, 400, str(error))

        elif isinstance(data, list):
            #
            # Bulk creation of many user ressources
            #
            transaction = await transactions.start_transaction()
            try:
                new_users = [User.structure(item) for item in data]
                # TODO: Is there a limit of how many users can be created in a single call?
                await User.bulk_create(new_users)
                logger.info("Commiting %s new users.", len(new_users))
                await transaction.commit()
                resp.status_code = 201
                return
            except IntegrityError as error:
                logger.error(
                    "Creation of %s new users failed. Rolling back. %s", len(new_users), error
                )
                await transaction.rollback()
                error_response(resp, 409, str(error))
            except Exception as error:  # pylint: disable=W0703
                logger.error(
                    "Creation of %s new users failed. Rolling back. %s", len(new_users), error
                )
                await transaction.rollback()
                error_response(resp, 400, str(error))
        else:
            resp.status_code = 400

    async def on_delete(self, req: Request, resp: Response):
        await User.all().delete()
