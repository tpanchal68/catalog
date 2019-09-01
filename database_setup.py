from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class DishName(Base):
    __tablename__ = 'dishname'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    course = Column(String(250))
    region = Column(String(250))
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'course': self.course,
            'region': self.region,
        }


class RecipeIngredients(Base):
    __tablename__ = 'recipeIngredients'

    id = Column(Integer, primary_key=True)
    ingredients = Column(String(80), nullable=False)
    quantity = Column(String(25))
    measure = Column(String(25))
    dishname_id = Column(Integer, ForeignKey('dishname.id'))
    dishname = relationship(DishName)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'ingredients': self.ingredients,
            'quantity': self.quantity,
            'id': self.id,
            'measure': self.measure,
        }


class RecipeMethod(Base):
    __tablename__ = 'recipeMethod'

    id = Column(Integer, primary_key=True)
    steps = Column(String(250), nullable=False)
    dishname_id = Column(Integer, ForeignKey('dishname.id'))
    dishname = relationship(DishName)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'steps': self.steps,
            'id': self.id,
        }


basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'recipecatalog.db'))
Base.metadata.create_all(engine)
