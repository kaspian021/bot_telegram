from sqlalchemy import Column
from sqlalchemy import String,Integer,Boolean
from database.database import Base

class Users(Base):
    __tablename__ = 'users'
    
    
    id = Column(Integer,index=True,primary_key=True)
    chatid= Column(Integer,nullable=False,unique=True)
    name = Column(String,)
    isBadWord= Column(Integer,index=True,nullable=False)
    isBlock = Column(Boolean,nullable=False)