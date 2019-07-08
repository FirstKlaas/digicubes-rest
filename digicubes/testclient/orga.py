import requests
import json


class UserProxy:
    __writable_fields__ = ["login", "firstName", "lastName", "email", "isActive", "isVerified"]
    __readable_fields__ = ["id", "created_at", "modified_at"]
    __slots__ = ["data"] + __writable_fields__ + __readable_fields__

    def __init__(self, data={}):
        self.data = data

    def __getattribute__(self, attr):
        if attr in UserProxy.__writable_fields__ or attr in UserProxy.__readable_fields__:
            return self.data[attr]
        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        if attr in UserProxy.__readable_fields__:
            raise KeyError(f"Attribute {attr} is not writable.")

        if attr in UserProxy.__writable_fields__:
            self.data[attr] = value
        else:
            object.__setattr__(self, attr, value)

    def __str__(self):
        return f"[{self.id}] {self.login} ({self.lastName},{self.firstName})"

    def __repr__(self):
        return f"UserProxy({self.data})"

    def delete(self):
        Org.delete_user(self.id)

    def create(self):
        Org.create_user(self)


class DigiCubeServer:

    url = None

    @classmethod
    def init(cls, url):
        cls.url = url
        cls.Org = Org
        Org.url = url + "/users/"


class Org:

    url = None

    @classmethod
    def new_user(cls, data={}):
        return UserProxy(data)

    @classmethod
    def get_user(cls, id, filtered_fields=None, links=False):
        headers = {"content-type": "application/json", "x-hateoa": str(links).lower()}

        if filtered_fields is not None:
            headers["x-filter-fields"] = ",".join(filtered_fields)

        # print(headers)
        result = requests.get(f"{cls.url}{id}", headers=headers)
        if result.status_code == 200:
            return UserProxy(result.json())

    @classmethod
    def delete_user(cls, id):
        result = requests.delete(f"{cls.url}{id}")
        if result.status_code != 200:
            raise ValueError(f"Could not delete user with id {id}")

    @classmethod
    def create_user(cls, user: UserProxy):
        headers = {"content-type": "application/json"}
        result = requests.post(f"{cls.url}", headers=headers, json=user.data)
        if result.status_code == 201:
            user.data = result.json()
        else:
            raise ValueError("Could not create user")

    @classmethod
    def get_users(cls, filtered_fields=None):
        headers = {"content-type": "application/json", "x-hateoa": "false"}
        if filtered_fields is not None:
            headers["x-filter-fields"] = ",".join(filtered_fields)

        result = requests.get(f"{cls.url}", headers=headers)
        if result.status_code == 200:
            return [UserProxy(data) for data in result.json()]

        raise ValueError("Cannnot get users")
