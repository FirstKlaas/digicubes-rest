# pylint: disable=redefined-outer-name
#
import logging
from typing import Generator

import pytest
from tortoise import Tortoise
from pydantic import ValidationError

from digicubes_rest.model import SchoolModel, CourseModel

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
async def orm() -> Generator:
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"model": ["digicubes_rest.storage.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="function")
async def test_school() -> SchoolModel:
    school = await SchoolModel.create(name="test school")
    yield school
    await school.delete()


@pytest.mark.asyncio
async def test_create_school() -> None:
    # Check if we have no initial schools
    schools = await SchoolModel.all()
    assert len(schools) == 0
    # Create a test school
    school_name = "    test school   "
    school = await SchoolModel.create(name=school_name, description="simple description")
    assert school.name == school_name.strip(), "School names are not equal."
    # Check if we hav exactly one school
    schools = await SchoolModel.all()
    assert len(schools) == 1, "Expected exactly 1 school in the database"
    db_school = await SchoolModel.get(name=school_name.strip())
    assert db_school.created_at is not None
    courses = await db_school.get_courses()
    assert len(courses) == 0

@pytest.mark.asyncio
async def test_create_course(test_school:SchoolModel) -> None:
    # Check if we have no initial courses
    courses = await CourseModel.all()
    assert len(courses) == 0
    # Create a test course
    course_name = "    test course   "
    course = await test_school.create_course(name=course_name, description="simple description")
    assert course.name == course_name.strip(), "Course names are not equal."
    # Check if we hav exactly one school
    courses = await CourseModel.all()
    assert len(courses) == 1, "Expected exactly 1 course in the database"
    db_course = await CourseModel.get(name=course_name.strip())
    assert db_course.created_at is not None

