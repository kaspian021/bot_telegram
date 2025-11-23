from dependense.orm import get_bot
from telebot import types
from settings import settings




def all_button_for_Admin():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2,)
    bot = get_bot()
    
    btn1= types.KeyboardButton('/AllUser')
    btn2 = types.KeyboardButton('/AllUserBlock')
    
    keyboard.add(btn1,btn2)
    
    bot.send_message(settings.CHAT_ID,'رئیس لطفا شما از این دکمه ها استفاده کنید🙂‍',reply_markup=keyboard)
    

def button_for_unblock_requestsUser(chat_id:int):
    keyboard= types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    
    bot = get_bot()
    
    btn_unblock = types.KeyboardButton(f'/unblock:{chat_id}')
    
    keyboard.add(btn_unblock)
    
    bot.send_message(settings.CHAT_ID,'رئیس شما میتونید با زدن دکمه: /unblock: کاربر رو از بلاکی دربیارید🙂',reply_markup=keyboard)