from random import randint
from pydantic import EmailStr
from sqlalchemy import Column, String, Integer, Boolean
# from database import Base
from pydantic import BaseModel

class users(BaseModel):
    username: str
    email: str
    password: str
  
class Blog(BaseModel):
    id: int
    user_id :int
    username: str
    title:str
    content: str
    
    
class login(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

