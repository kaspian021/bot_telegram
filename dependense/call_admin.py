
from dependense.orm import get_bot
from settings import settings


def meessage_checkAdmin(chat_id:int)->bool:
    
    if chat_id == settings.CHAT_ID:
        
        return True
    else:
        return False
    

def message_Admin(text:str):
    bot = get_bot()
    
    bot.send_message(settings.CHAT_ID,text=text)


def message_unBlockForAdmin(chat_id:int,userName:str)->bool:
    try:
        bot = get_bot()
        bot.send_message(settings.CHAT_ID,f' رئیس کاربری با این مشخصات میخواد از بلاکی در بیاد: \nName: {userName}\nchat_id: {chat_id}\n')

        return True
    
    except Exception as e:
        print(f'Error Send: {e}')
        return False
    



    
    