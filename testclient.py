"""
Test client. Obsolet, when all test are written
"""
from datetime import time

from digicubes.client.proxy import UserProxy, SchoolProxy
from digicubes.client import DigiCubeClient
from digicubes.client.service.exceptions import ConstraintViolation

if __name__ == "__main__":
    client = DigiCubeClient('http://localhost:5042')

    User = client.user_service
    Role = client.role_service
    Right = client.right_service
    School = client.school_service

    user = User.get(2)

    print("-" * 40)
    print(user)

    print("-" * 40)
    for user in User.all():
        print(user)

    print("-" * 40)
    try:
        User.create(UserProxy('yolo'))
    except ConstraintViolation as e:
        print(e)

    print("-" * 40)
    User.create_bulk([UserProxy(f"gen_{time.time()}") for _ in range(10)])

    print("-" * 40)
    for user in User.all():
        print(user)

    print("-" * 40)
    print(" DELETE all Users")
    print("-" * 40)
    # User.delete_all()

    print("-" * 40)
    for user in User.all():
        print(user)

    print("-" * 40)
    print(" R O L E S")
    print("-" * 40)

    for role in Role.all():
        print(role)

    print("-" * 40)
    print(Role.get(1))

    print("-" * 40)
    print(" R I G H T S")
    print("-" * 40)

    for right in Right.all():
        print(right)

    print("-" * 40)
    print(" S C H O O L ")
    print("-" * 40)
    schools = [SchoolProxy(name="TGG1"), SchoolProxy(name="UEG1")]
    print(schools)
    try:
        School.create_bulk(schools)
    except ConstraintViolation as error:
        print(error)
