# pylint: disable=redefined-outer-name
#
import logging
from typing import Generator

import pytest
from tortoise import Tortoise
from pydantic import ValidationError

from digicubes_rest.model import SchoolModel, CourseModel, UnitModel

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

@pytest.fixture(scope="function")
async def test_course(test_school: SchoolModel) -> CourseModel:
    course = await test_school.create_course(name="test course", description="test description")
    yield course
    await course.delete()

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

@pytest.mark.asyncio
async def test_create_unit(test_course: CourseModel) -> None:

    units = await UnitModel.all()
    assert len(units) == 0

    unit_name = "  test_unit  "
    unit = await test_course.create_unit(name=unit_name)
    assert unit.name == unit_name.strip()

    units = await UnitModel.all()
    assert len(units) == 1

    await unit.delete()

    units = await UnitModel.all()
    assert len(units) == 0

@pytest.mark.asyncio
async def test_course_parent(test_school: SchoolModel, test_course: CourseModel) -> None:

    school = await test_course.get_school()
    assert school.name == test_school.name

    courses = await test_school.get_courses()
    assert len(courses) == 1
    assert courses[0].name == test_course.name

    second_course = await test_school.create_course(name="second course")
    courses = await test_school.get_courses()
    assert len(courses) == 2
    await second_course.delete()
    courses = await test_school.get_courses()
    assert len(courses) == 1

