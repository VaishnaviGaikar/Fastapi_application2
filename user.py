from fastapi import APIRouter,HTTPException,Depends,status
from typing import List
import Schemas,models,database,hashing
from sqlalchemy.orm import Session

router=APIRouter(
    tags=['user'],
    prefix='/user'

)

# @router.post('/')
# def create_User(request:Schemas.users,db:Session=Depends(database.get_db)):
#     new_user=models.create_user(name=request.name,password=hashing.hash.bcrypt(request.password),email=request.email)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

@router.get('/')
def get_all_user(db:Session=Depends(database.get_db)):
    get_all=db.query(models.create_user).all()
    return get_all