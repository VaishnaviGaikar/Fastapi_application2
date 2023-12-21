from random import randint
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class create_user(Base):
    __tablename__ = "users1"
    email = Column(String(255), unique = True)
    username = Column(String(200), unique = True)
    password = Column(String(255), unique = False)
    id = Column(Integer, primary_key= True)
    is_verified = Column(Boolean, nullable = True)
    verification_code = Column(Integer,nullable=True)
    is_active =Column(Boolean, nullable = True)
    Blogs = relationship("Blog", back_populates="owner")

    
class Blog(Base):
    __tablename__ = "Blog1"
    id = Column(Integer, unique = True, primary_key= True)
    user_id = Column(Integer, ForeignKey('users1.id'))
    username = Column(String(255))
    content = Column(String(255))
    title = Column(String(200), index=True)
    owner = relationship("create_user", back_populates="Blogs")
