# pylint: disable=C0111
import logging

from responder.core import Request, Response
from tortoise.exceptions import IntegrityError
from tortoise import transactions

from digicubes.storage.models import User
from .util import BasicRessource, error_response

logger = logging.getLogger(__name__)  # pylint: disable=C0103

logger = logging.getLogger(__name__)


class UsersRessource(BasicRessource):
    """
    Supported verbs:

    +------------+--------------------+
    | ``GET``    | Request all users  |
    +------------+--------------------+
    | ``POST``   | Create new user(s) |
    +------------+--------------------+
    | ``DELETE`` | Delete all users   |
    +------------+--------------------+

    """

    async def on_get(self, req: Request, resp: Response):
        """
        Requesting all users.
        if the header field ``X-HATEOAS`` is available, hyperlinks for
        the ressources in the respond will be generated.

        Possible values for the header field:

        self: only the link to get the ressouce will be generated
        """
        filter_fields = self.get_filter_fields(req)
        users = [user.unstructure(filter_fields) for user in await User.all()]
        resp.media = users

    async def on_post(self, req, resp):
        """
        Creates new user(s). The user data is defined as json object in the
        body of the request. You can create a single user or a group of users.
        When creating a bulk of users, the json object in the body has to be
        an array.

        Sample for creating a single user:

        .. code-block:: json

            {
                "login"     : "diggi",
                "email"     : "sam@diggicubes.org",
                "firstName" : "Samantha",
                "lastName"  : "Miller"
            }

        Only the ``login`` attribute is mandatory. So the smallest user definition would be:

        .. code-block:: json

            {
                "login"     : "diggi"
            }

        If you want to create multiple users, simply put user json object in an array.

        If a model constraint gets violated, a status code of 409 will be send back. In
        case of a bulk update, if any of the users violates a constraint, none of the
        users will created. This operation is atomic.

        If we do not know how to handle the json object, a status code of 400 is send
        back.
        """

        #
        # POST
        #
        # Creating new Ressources
        #
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
                return
            except IntegrityError:
                error_response(
                    resp, 409, f"User with login {login} already exists. Login must be unique."
                )
                return
            except Exception as e:
                error_response(resp, 500, str(e))
                return

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
                error_response(resp, 500, str(error))
        else:
            resp.status_code = 400

    async def on_delete(self, req, resp):
        """
        This operation will delete every (!) user in the database.

        .. warning::
            Like all the other operations, this operation is undoable. All users will
            be deleted. So think twice before calling it.

        """
        try:
            await User.all().delete()
        except Exception as error:
            error_response(resp, 500, str(error))
