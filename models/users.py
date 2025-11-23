from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    name:str=''
    isBadWord:int = 0
    isBlock:bool=False
    

class UserCreate(UserBase):
    chatId:int
    
    class Config:
        from_attributes=True


class UserUpdate(BaseModel):
    name:str=''
    isBadWord:int = 0
    isBlock:bool=False
    
    class Config:
        from_attributes=True



class GetUser(UserBase):
    chatId:int

    
    class Config:
        from_attributes=True


class GetAllUser(BaseModel):
    all_user : list[GetUser]
    
    class Config:
        from_attributes=True
        
        

class show_user(BaseModel):
    name:str
    isBadWord:int
    
    