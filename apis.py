from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session
from random import randint
from models import create_user
from Schemas import Blog, users
from email.message import EmailMessage
import smtplib
# from auth import get_current_active_user
# from auth import password_hashing, create_access_token
from typing import List
# from blog import Blog
# from auth import get_current_active_user
from database import get_db

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import models
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter()

blogs_db = {}

users_db = {}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str 


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 
    
def verify_password(user, password):
    if user.password == password:
        return True 
    # return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    user = db.query(models.create_user).filter(models.create_user.username == username).first()
    return user
    # if username in models.create_user:
    #     user_dict = db[username]
    #     return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(user, password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     encoded_jwt = jwt.decode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise Exception("username is not valid")
        token_data = TokenData(username=username)
    except JWTError:
        raise Exception("not valid")
    user = get_user(get_db, username=token_data.username)
    if user is None:
        raise Exception("not valid")
    return user

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     return token.verify_token(token,credentials_exception)


@router.post("/register",response_model=None)
def register_user(user: users):
    if get_db.query(create_user).filter(create_user.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # hashed_password = password_hashing.hash(user.password)
    # hashed_password = "cd9ced8aa59f2a4ad68595690043ff6e5bb1d158c67a38bef9e72b1671c2bc55"
    
    verification_code = str(randint(100000, 999999))

    const_mail = "gaikarvaishnavi5@gmail.com"
    const_password = "blgwgrnrckyqhfry"
    
    msg = EmailMessage()
    msg['Subject'] = "OTP Verification"
    msg['From'] = "gaikarvaishnavi5@gmail.com"
    msg['To'] = user.email
    msg.set_content(
        f"Verification Code: {verification_code}")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(const_mail, const_password)
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    db_user = create_user(username=user.username, email=user.email, password=user.password, verification_code=verification_code, is_verified = False, is_active = False)
    get_db.add(db_user)
    get_db.commit()

    return {"Msg":"Registration successful"}

@router.post("/verify-email/{user_id}")
def verify_email(user_name: str, otp: int):
    user = get_db.query(create_user).filter(create_user.username == user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    if user.verification_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.is_verified = True
    get_db.commit()
    data = {"detail": "Email verified successfully"}
    return data


# @router.post("/login", response_model=None)
# def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db())
# ):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}
# @router.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db())
# ):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/blog", response_model=None)
# def create_blog(username:str, content:str):
#     user = get_db.query(create_user).filter( create_user.username == username).first()
#     if not user or not create_user.is_verified:
#         raise HTTPException(status_code=401, detail="User not verified")
#     return {"username": username, "content": content}

# @router.put("/blog/{blog_username}", response_model=None)
# def update_blog(blog_username: str, blog: Blog, current_user: str = Depends(users), db: Session = Depends(get_current_user)):
#     if blog_username not in blogs_db:
#         raise HTTPException(status_code=404, detail="Blog not found")
#     if blogs_db[blog_username].username != current_user:
#         raise HTTPException(status_code=403, detail="Permission denied")
#     blogs_db[blog_username].content = blog.content
#     return blogs_db[blog_username]


# @router.delete("/blog/{blog_id}", response_model=Blog)
# def delete_blog(blog_username: str, current_user: str = Depends(users), db: Session = Depends(get_current_user)):
#     if blog_username not in blogs_db:
#         raise HTTPException(status_code=404, detail="Blog not found")
#     if blogs_db[blog_username].username != current_user:
#         raise HTTPException(status_code=403, detail="Permission denied")
#     deleted_blog = blogs_db.pop(blog_username)
#     return deleted_blog

# # Blog read-only operations for all users
# # @router.get("/blogs", response_model=None)
# # def get_all_blogs():
# #     blogs = db.query.session(Blog.content).all()
# #     return blogs

# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     return current_user


# @router.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]