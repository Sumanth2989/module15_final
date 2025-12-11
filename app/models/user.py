from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, synonym
from .base_class import Base # only from base_class


class User(Base):
    __tablename__ = "users"

    # store primary key in DB column 'user_id' but expose attribute 'id' (tests expect User(id=...))
    id = Column('user_id', Integer, primary_key=True, index=True)
    # keep email column name the same
    email = Column(String, unique=True, index=True, nullable=False)
    # store password in DB column 'password' but expose as 'hashed_password' for tests
    hashed_password = Column('password', String, nullable=False)

    # Backwards compatibility for code that uses user.user_id or user.password
    user_id = synonym('id')
    password = synonym('hashed_password')

    calculations = relationship("Calculation", back_populates="owner")
