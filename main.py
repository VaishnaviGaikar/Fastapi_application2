from email.message import EmailMessage
from random import randint
import smtplib
from fastapi import APIRouter, FastAPI,Depends,HTTPException,status
import database
import models
import Schemas
from database import Session,get_db
from sqlalchemy.orm import Session
import blog
import user
import auth

app=FastAPI()
router = APIRouter()

@app.post("/register",response_model=None)
def register_user(user: Schemas.users):
    if database.db.query(models.create_user).filter(models.create_user.email == user.email).first():
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
    
    db_user = models.create_user(username=user.username, email=user.email, password=user.password, verification_code=verification_code, is_verified = False, is_active = False)
    database.db.add(db_user)
    database.db.commit()

    return {"Msg":"Registration successful"}

@app.post("/verify-email/{user_id}")
def verify_email(user_name: str, otp: int):
    user = database.db.query(models.create_user).filter(models.create_user.username == user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    if user.verification_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.is_verified = True
    database.db.commit()
    data = {"detail": "Email verified successfully"}
    return data

app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(user.router)







