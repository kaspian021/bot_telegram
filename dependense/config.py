

from telebot import TeleBot
from dependense.orm import get_db
from models.users import GetAllUser, GetUser, UserCreate, UserUpdate
from schemas.users import Users
from telebot.types import ChatPermissions
from sqlalchemy import Select


def isBadWordAddDB(id:int)->int:
    with get_db() as db:
        
        result= db.query(Users).filter(Users.chatid==id).first()
        
        if result:
            
            db.query(Users).filter(Users.chatid==id).update({Users.isBadWord:Users.isBadWord+1})
            updating_user= db.query(Users.isBadWord).filter(Users.chatid==id).scalar()
            
            
            return int(updating_user)
        else:
            new_user = Users(chatid=id,isBadWord=1,isBlock=False,numberRequestsUnblock=0)
            
            db.add(new_user)
            
            return 1
    

def isCheckBadWordDB(id:int):
    with get_db() as db:
        result = db.query(Users).filter(Users.chatid==id).first()
        if result:
            resultBadWord= db.query(Users.isBadWord).filter(Users.chatid==id).scalar()
        
            if resultBadWord >0:
                return int(resultBadWord)
        
            else:
                return 0
        else:
            new_user = Users(chatid=id,isBadWord=0,isBlock=False,numberRequestsUnblock=0)
            
            db.add(new_user)
            return 1
    

# def blockUser(bot:TeleBot,user_id:int,chat_id:int,)-> bool:
#     """
#         متد بلاک کردن کاربر و همینطور حذف ان از دیتا بیس
    
#     """

#     try:
#         permission= ChatPermissions(
#             can_send_messages=False,
#             can_send_media_messages=False,
#             can_send_polls=False,
#             can_send_other_messages=False,
#             can_add_web_page_previews=False,
#             can_change_info=False,
#             can_invite_users=False,
#             can_pin_messages=False
#         )

#         bot.restrict_chat_member(
#             chat_id=chat_id,
#             user_id=user_id,
#             permissions=permission,
#             until_date=None
#         )

#         return True
    

#     except TelegramError as e:
#         print(f'Error: TelegramError {e}')
#         return False


def deleteUser(chat_id:int,):
    with get_db() as db:
        result = db.query(Users).filter(Users.chatid==chat_id).first()
    
        db.delete(result)
    

def updateUser(chat_id:int, data:UserUpdate) -> bool:
    try:
        with get_db() as db:
            user = db.query(Users).filter(Users.chatid==chat_id).first()
            if not user:
                return False

            # چاپ مقادیر قبل و بعد برای دیباگ
            print(f"[UpdateUser] قبل: {user.isBlock}")

            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(user, key, value)

            db.add(user)  # اطمینان از ثبت تغییرات
            print(f"[UpdateUser] بعد: {user.isBlock}")

            return True
    except Exception as e:
        print(f"Error UpdateUser: {e}")
        return False


        
        
def get_All_user()->GetAllUser:
    try:
        with get_db() as db:
            select = Select(Users)
            result = db.scalars(select).all()
            if result:
                first_item = result[0]
                allData = []
                for item in result:
                    
                    allData.append(GetUser(
                        chatId=int(item.chatid), 
                        name=str(item.name),      
                        isBadWord=int(item.isBadWord),  
                        isBlock=bool(item.isBlock)  
                    ))
                
                return GetAllUser(all_user=allData)
            else:
                return GetAllUser(all_user=[])
    
    except Exception as e:
        print(f'Error get_All_user: {e}')
        return GetAllUser(all_user=[])
        
        
        
        
def get_All_user_Block():
    try:
        with get_db() as db:
        
            select = Select(Users).where(Users.isBlock==True)
            result = db.scalars(select).all()
            
            allData = []
            for item in result:
                allData.append(GetUser(
                    chatId=int(item.chatid),  
                        name=str(item.name),      
                        isBadWord=int(item.isBadWord),  
                        isBlock=bool(item.isBlock) 
                ))
            
            return GetAllUser(all_user=allData)
    
    except Exception as e:
        print(f'Error get_All_user_Block: {e}')
        return GetAllUser(all_user=[])
        
 

def isRequestsblock(chatId:int)->bool:       
    with get_db() as db:
    
        result = db.query(Users.numberRequestsUnblock).filter(Users.chatid==chatId).scalar()
        
        if result==0:
            return True
        else:
            return False
    


def check_block_user(chatId:int)-> bool:
    with get_db() as db:
    
        result = db.query(Users.isBlock).filter(Users.chatid==chatId).scalar()
        
        if result:
            return True
        else:
            return False