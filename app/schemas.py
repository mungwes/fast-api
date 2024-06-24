from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    email:EmailStr
    password:str
    
class UserResponse(BaseModel):
    id:int
    email:EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    
class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse
    
    class Config:
        orm_mode = True
        
class PostVote(BaseModel):
    Post: PostResponse
    votes: int 
    
    class Config:
        orm_mode = True
        
class UserLogin(BaseModel):
    email:EmailStr
    password: str

    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        orm_mode = True
    
class TokenData(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    
class Vote(BaseModel):
    post_id: int
    dir: Literal[0,1]
    