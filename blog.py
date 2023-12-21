from fastapi import APIRouter,HTTPException,Depends,status
import Schemas
import models
import database
from sqlalchemy.orm import Session

from oauth2 import get_current_user

router=APIRouter(
    tags=['Blog'],
    prefix='/blog'
)

@router.post('/')
def create_blog(request:Schemas.Blog,db:Session=Depends(database.get_db),auth=Depends(get_current_user)):
    
    new_blog=models.Blog(
        id = request.id,\
        user_id = request.user_id,
        username = request.username,
        title=request.title,
        content = request.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put('/{id}')
def update_blog(id:str,request:Schemas.Blog,db:Session=Depends(database.get_db),current_user:models.create_user=Depends(get_current_user)):
    upd_blog=db.query(models.Blog).filter(models.Blog.id==id)
    if not upd_blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No user found to update")
    upd_blog.update(title=request.title,desc=request.desc,author=request.author)
    db.commit()
    return "Updated Successful"

@router.delete('/{id}')
def del_blog(id:str,db:Session=Depends(database.get_db),current_user:models.create_user=Depends(get_current_user)):
    del_blog=db.query(models.Blog).filter(models.Blog.blog_id==id).delete(synchronize_session=False)
    db.commit()
    return f"blog with  id no {id} is deleted"

@router.get('/{id}')
def get_blog(id:str,db:Session=Depends(database.get_db),current_user:models.create_user=Depends(get_current_user)):
    get_blog=db.query(models.Blog).filter(models.Blog.id==id).first()
    if not get_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No user found with id no {id}")
    return get_blog