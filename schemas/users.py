from sqlalchemy import Column
from sqlalchemy import String,Integer,Boolean,BigInteger
from database.database import Base

class Users(Base):
    __tablename__ = 'users'
    
    
    id = Column(Integer,index=True,primary_key=True)
    chatid= Column(BigInteger,nullable=False,unique=True)
    name = Column(String(255))
    isBadWord= Column(Integer,index=True,nullable=False,default=0)
    isBlock = Column(Boolean,nullable=False)
    numberRequestsUnblock= Column(Integer,nullable=False,index=True,default=0)