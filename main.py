import responder

from sqlalchemy import (
        create_engine, Column, Integer, String
    )

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.ext.declarative import declarative_base

from user import init as user_init

api = responder.API()
engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class NoSuchElement(Exception):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __str__(self):
        return f"{self.name} [{self.id}]"

    def __repr__(self):
        return f"User(name='{self.name}')"

    @classmethod
    def get(cls, session, id):
        #session = Session()
        try:
            return session.query(cls).filter(cls.id == id).one()
        except NoResultFound:
            raise NoSuchElement(f"No {cls.__name__} with id {id} found.")
        

Base.metadata.create_all(engine)

u = User(name='Klaas')
session = Session()
session.add(u)
session.commit()

session = Session()
me = User.get(session, 1)
me.name = 'Marion'
print(me.name)
session.commit()

with Session() as session:
    me = User.get(session, 1)
    print(me)
    me.name = 'kdsk'
    session.commit()

user_init(api)

@api.route("/moin/{name}")
async def moin(req,resp, *, moin, name):
    resp.text = f"hier, {name}"
 
if __name__ == "__main__":
    api.run()
