from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import database,models,token_1
from token_1 import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from database import get_db

router=APIRouter(
    tags=['Authentication']
)
@router.post("/token")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.create_user).filter(models.create_user.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No user found")

    # if not hash.verify(request.password, user.password):
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wrong Credentials")

    access_token = token_1.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}