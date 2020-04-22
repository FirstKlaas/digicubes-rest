import logging

from responder.core import Request, Response
from tortoise.exceptions import DoesNotExist

from digicubes_rest.storage import models
from .util import BasicRessource, needs_int_parameter, error_response, needs_bearer_token

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class CourseRessource(BasicRessource):
    """
    Endpoint for a course.
    """

    @needs_int_parameter("course_id")
    @needs_bearer_token()
    async def on_post(self, req: Request, resp: Response, *, course_id: int) -> None:
        """
        405 Method not allowed
        """
        try:
            resp.status_code = 405
            resp.headers["Allow"] = "GET, PUT, DELETE"
            resp.text = ""

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("course_id")
    @needs_bearer_token()
    async def on_get(self, req: Request, resp: Response, *, course_id: int):
        """
        Get a single school

        :param int course_id: The id of the requested course.
        """
        try:
            course = await models.Course.get(id=course_id)
            resp.media = course.unstructure(self.get_filter_fields(req))
            self.set_timestamp(resp, course)

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))

    @needs_int_parameter("course_id")
    @needs_bearer_token()
    async def on_put(self, req: Request, resp: Response, *, course_id: int) -> None:
        """
        Updates the course.

        The current course, specified by the ``course_id`` is updated
        the the json data of the body.

        The fields id, created_at, modified_at are ignored, as they can 
        not be updated.
        """
        data = await req.media()

        # That's not the most elegant version. The two
        # attributes are write protected, so I pop
        # the two values from the data dict (if present).
        data.pop("created_at", None)
        data.pop("modified_at", None)

        # We also pop the id of the provided json data
        # as we want to make shure, that the id of the
        # url is used.
        data.pop("id", None)

        if not isinstance(data, dict):
            resp.status_code = 400  # Bad_Request
            resp.text = "Bad formatted body content"
            return

        try:
            course: models.Course = await models.Course.get(id=course_id)

            course.update(data)
            course.id = int(course_id)
            logger.debug(data)
            await course.save()
            filter_fields = self.get_filter_fields(req)
            resp.media = course.unstructure(filter_fields)
            resp.status_code = 200

        except DoesNotExist:
            error_response(resp, 404, f"No course with id {course_id} found.")

        except Exception as error:  # pylint: disable=W0703
            logger.exception("Could not update course.")
            error_response(resp, 500, str(error))

    @needs_int_parameter("course_id")
    @needs_bearer_token()
    async def on_delete(self, req: Request, resp: Response, *, course_id: int):
        """
        Delete a course specified by its id. If the course does not exisi, a 404
        status code is send back.

        :param int course_id: The id of the course to be deleted
        """
        try:
            logger.debug("Trying to delete course %d", course_id)
            course = await models.Course.get(id=course_id)
            await course.delete()
            filter_fields = self.get_filter_fields(req)
            resp.media = course.unstructure(filter_fields)
        except DoesNotExist:
            error_response(resp, 404, f"Course with id {course_id} does not exist.")

        except Exception as error:  # pylint: disable=W0703
            error_response(resp, 500, str(error))
