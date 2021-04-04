# pylint: disable=redefined-outer-name
#
import logging
import os
from typing import Generator

import pytest
from pydantic import ValidationError
from tortoise import Tortoise

from digicubes_rest.exceptions import QueryError
from digicubes_rest.model import CourseModel, SchoolModel, UnitModel
from digicubes_rest.storage import create_schema, init_orm, shutdown_orm

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function", autouse=True)
async def orm() -> Generator:
    os.environ["DIGICUBES_DATABASE_URL"] = "sqlite://:memory:"

    await init_orm()
    await create_schema()
    yield
    await shutdown_orm()


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
async def test_create_course(test_school: SchoolModel) -> None:
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


@pytest.mark.asyncio
async def test_find_course(test_school: SchoolModel, test_course: CourseModel) -> None:

    courses = await test_school.find_courses(name=test_course.name)
    assert len(courses) == 1
    course = courses[0]
    assert course is not None
    assert course.name == test_course.name
    assert course.id is not None

    with pytest.raises(QueryError):
        await test_school.find_courses(YYY="XXX")

    courses = await test_school.find_courses(name="XXX")
    assert len(courses) == 0

    await test_school.create_course(name="C01 jjfj")
    await test_school.create_course(name="C02 inside ee")
    await test_school.create_course(name="C03 djksfhjdfee")
    await test_school.create_course(name="D01 rtirieE", is_private=True)

    assert len(await CourseModel.all()) == 5

    courses = await test_school.find_courses(name__startswith="C0")
    assert len(courses) == 3

    courses = await test_school.find_courses(name__contains="ksfh")
    assert len(courses) == 1

    courses = await test_school.find_courses(name__contains="This is not a name")
    assert len(courses) == 0

    courses = await test_school.find_courses(name__iendswith="ee")
    assert len(courses) == 3

    courses = await test_school.find_courses(is_private=False)
    assert len(courses) == 4

    courses = await test_school.find_courses(is_private=True)
    assert len(courses) == 1


@pytest.mark.asyncio
async def test_crud_unit(test_course: CourseModel) -> None:

    assert len(await test_course.get_units()) == 0
    unit_name = "  Test Unit  "
    unit = await test_course.create_unit(name=unit_name)
    assert len(await test_course.get_units()) == 1
    assert unit.created_at is not None
    assert unit.name == unit_name.strip()
    await test_course.create_unit(name="U2 Unit")
    assert len(await UnitModel.all()) == 2
    assert len(await test_course.get_units()) == 2
    await unit.delete()
    assert len(await UnitModel.all()) == 1
    assert len(await test_course.get_units()) == 1
    for name in ["U3 Unit", "U4 Demo", "U5 Demo B"]:
        await test_course.create_unit(name=name)

    assert len(await test_course.get_units()) == 4
    assert len(await test_course.find_units(name="U4 Demo")) == 1
    assert len(await test_course.find_units(name__startswith="U")) == 4
    assert len(await test_course.find_units(name__endswith="emo")) == 1
    assert len(await test_course.find_units(name__contains="emo")) == 2

    units = await test_course.find_units(name="U2 Unit")
    assert len(units) == 1
    unit = units[0]
    assert unit.name == "U2 Unit"
    await unit.update(name="Digicubes")

    units = await test_course.find_units(name="Digicubes")
    assert len(units) == 1
    assert units[0].id == unit.id
