from telebot import types

from dependense.config import updateUser
from dependense.orm import get_bot
from models.users import UserCreate, UserUpdate

keyboard= types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)


def unblock_button(chat_id:int):
    bot = get_bot()
    updateUser(chat_id=chat_id,data=UserUpdate(isBlock=True))
    btnUnblock= types.KeyboardButton('/unblock')
    keyboard.add(btnUnblock)
    bot.send_message(chat_id,'شما مجبورید ریکوست برای انبلاک شدن بفرستین!!',reply_markup=keyboard)


def start_Button(chat_id:int):
    bot = get_bot()
    
    btnInformation= types.KeyboardButton('/information')
    btnReadMe= types.KeyboardButton('/about')
    keyboard.add(btnInformation,btnReadMe)
    bot.send_message(chat_id,'بهتره هرچیزی که میخوای بگی راجب کار باشه ممنون میشم🙂',reply_markup=keyboard)


def next_unblock_button(chatId:int):
    bot = get_bot()
    keyboard= types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    btnInformation= types.KeyboardButton('/information')
    btnReadMe= types.KeyboardButton('/about')
    keyboard.add(btnInformation,btnReadMe)
    bot.send_message(chatId,'بهتره هرچیزی که میخوای بگی راجب کار باشه ممنون میشم🙂',reply_markup=keyboard)
   
