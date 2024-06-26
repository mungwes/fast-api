from typing import List, Optional
from fastapi import  Response, status, HTTPException, Depends, APIRouter
from .. import models, oauth2, schemas
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db

#import psycopg2
#import psycopg
#from psycopg.rows import dict_row
#import time

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
    )

# while True:
#     try:
#         conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', 
#                                password='kutleng123', row_factory=dict_row)
#         cursor = conn.cursor()
#         print("Database connection was successful!")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print(f"Error: {error}")
#         time.sleep(2)

        
@router.get("/", response_model=List[schemas.PostVote])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""select * from post""")
    #posts = cursor.fetchall()
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).
                         label("votes")).join(models.Vote,models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).limit(limit).offset(skip).all()

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO post (title, content, published) VALUES(%s, %s, %s) RETURNING *""",(post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostVote)
def get_post(id:int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM post WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()    
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    
    post = db.query(models.Post, func.count(models.Vote.post_id).
                         label("votes")).join(models.Vote,models.Vote.post_id == models.Post.id,
                                              isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} was not found")
    
        
    return post

@router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
def delete_post(id:int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM post WHERE id = %s RETURNING *""",  (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
                                              
    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id:int, post_schema:schemas.PostUpdate, db:Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE post SET title = %s, content = %s, published = %s WHERE id = %s  RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    
    post_query.update(post_schema.dict(), synchronize_session=False)
    db.commit()

    return post