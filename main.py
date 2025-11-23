import json
from telebot import TeleBot,apihelper
import re
from Buttons.buttons_for_Admin import all_button_for_Admin, button_for_unblock_requestsUser
from dependense.const_attributes import text_information,text_ReadMe,list_word_friend,howAreyou,list_badword,work_list,random_text
from dependense.call_admin import meessage_checkAdmin, message_unBlockForAdmin, message_Admin
from dependense.config import check_block_user, deleteUser, get_All_user, get_All_user_Block, isBadWordAddDB, isCheckBadWordDB, updateUser
from models.users import UserCreate, UserUpdate
from settings import settings
import random
from dependense.orm import get_db
from schemas import users as table
from telegram import Update
from Buttons.buttons_for_User import next_unblock_button, start_Button, unblock_button
from dependense.ai_groq import classify_intent, detect_toxicity, groq_chat
from dependense.tools import detect_project_domain, groq_process_project




bot = TeleBot(token=settings.TOKEN_BOT)


@bot.message_handler(commands=['start','help'])
def start_bot(message):
   db = next(get_db())
   chatId= message.chat.id 
   try:
        if message.text == '/start':
            resultAdmin= meessage_checkAdmin(chatId)
            if resultAdmin:
                message_Admin('سلام رئیس خوش اومدی به ربات خودت🙂‍')
            else:
                result = db.query(table.Users).filter(table.Users.chatid==chatId).first()
                if result:
                    bot.send_message(chatId,f"سلام خوش برگشتی به ربات شخصی (Alikaspian)\nاطلاعات شما: \n\nنام:{message.from_user.first_name}\nتعداد اخطار: {result.isBadWord}")

                else:
                    result2 = table.Users(
                        chatid=chatId,
                        name= message.from_user.first_name,
                        isBadWord= 0,
                        isBlock=False,
                            
                    )
                    db.add(result2)
                    db.commit()
                    bot.send_message(chatId,f"🙂سلام {message.from_user.first_name}عزیز به ربات همکاری و شخصی (Alikaspian) خوش امدید")
                    
                    start_Button(chatId)
            
        elif message.text == '/help':
            bot.send_message(chatId,'🙂چطور میتونم بهتون کمک کنم؟')
   except apihelper.ApiTelegramException as e:
        if e.error_code == 403:
           deleteUser(chatId)
           print(f"کارگر {message.chat.id} ربات را بلاک کرده است")
        else:
            raise e
    
    
    
@bot.message_handler(commands=['AllUser','AllUserBlock'])
def admin_message_handler(m):
    text = m.text
    chatId = m.chat.id
    
    if text == '/AllUser':
        result = get_All_user()
        
        if result and result.all_user:
            message_text = "👥 <b>لیست تمام کاربران</b>\n\n"
            message_text += "┌───────────────┬─────────────────┬──────────────┬────────────────┐\n"
            message_text += "│<b>کلمات بد</b>│   <b>بلاک</b>    │ <b>نام</b>   │   <b>ردیف</b>  │\n"
            message_text += "├───────────────┼─────────────────┼──────────────┼────────────────┤\n"
            
            for i, user in enumerate(result.all_user, 1):
                name = user.name if len(user.name) <= 8 else user.name[:7] + "…"
                block_icon = "🔴" if user.isBlock else "🟢"
                badword_icon = user.isBadWord
                
                message_text += f"│  {i:2d}  │ {name:10} │   {block_icon}    │    {badword_icon}     │\n"
            
            message_text += "└───────┴────────────┴──────────┴────────────┘\n\n"
            message_text += f"📊 <i>تعداد کل: {len(result.all_user)} کاربر</i>"
            
        else:
            message_text = "🫤 کاربری یافت نشد"
            
        bot.send_message(chatId, message_text, parse_mode='HTML')
    
    elif text == '/AllUserBlock':
        result = get_All_user_Block()
        
        if result and result.all_user:
            blocked_users = [user for user in result.all_user if user.isBlock]
            if blocked_users:
                message_text = "🚫 <b>لیست کاربران بلاک شده</b>\n\n"
                
                for i, user in enumerate(blocked_users, 1):
                    message_text += f"▫️ <b>{i}. {user.name}</b>\n"
                    message_text += f"   🆔: <code>{user.chatId}</code>\n"
                    message_text += f"   🔞 کلمات بد: {user.isBadWord}\n"
                    message_text += "   ───────────────────\n"
                    button_for_unblock_requestsUser(user.chatId)
                message_text += f"\n📊 تعداد: {len(blocked_users)} کاربر"
                
            else:
                message_text = "✅ هیچ کاربر بلاک شده‌ای وجود ندارد"
        else:
            message_text = "✅ هیچ کاربر بلاک شده‌ای وجود ندارد"
            
        bot.send_message(chatId, message_text, parse_mode='HTML')
        


@bot.message_handler(commands=['unblock','information','about'])
def message_All_Button(m):
    chat_id= m.chat.id
    db=next(get_db())
    resultAdmin= meessage_checkAdmin(chat_id)
    if resultAdmin:
        all_button_for_Admin()
        
        

    else:
        
        result= db.query(table.Users).filter(table.Users.chatid==chat_id).first()
        if result:
        
            text= m.text
            
            if text == '/unblock':
                result_isBlock_user= check_block_user(chat_id)
                if result_isBlock_user:
                    
                    result_btn1= message_unBlockForAdmin(userName=str(result.name),chat_id=chat_id)
                    if result_btn1:
                        button_for_unblock_requestsUser(chat_id)
                        bot.send_message(chat_id,'درخواست آنبلاک برای ادمین با موفقیت ارسال شد منتظر نتیجه بمانید!!😒')
                else:
                    bot.send_message(chat_id,'شما بلاک نشده اید بنابراین نمیتونید از این دستور استفاده کنید🙂')
            if text == '/information':
                bot.send_message(chat_id,text=text_information, parse_mode='HTML')
            if text == '/about':
                bot.send_message(chat_id,text=text_ReadMe,parse_mode='HTML')

            

@bot.message_handler(regexp=r"^/unblock:\d{1,15}$")
def message_All_Admin(m):
    chatId= m.chat.id
    textAdmin = m.text
    if settings.CHAT_ID == chatId:
        is_unblock = any(unblock in textAdmin for unblock in ['/unblock','/removeBlock','/userUnBlock',])
        #بعدا چیز های بیشتری باید اضافه بشه برای عملیات های دیگه در سمت ادمین
        if is_unblock:
            ''
            resulttext = textAdmin.split(':')
            chatId_user= int(resulttext[1])
            result= updateUser(chat_id=chatId_user,data=UserUpdate(isBadWord=0,isBlock=False))
            
            if result:
                bot.send_message(chatId_user,'ادمین بررسی کرد و شمارو از بلاکی در اورد\nتبریک میگم شما دوباره میتونید راجب پروژه و بیزینس با من حرف بزنی🙂‍')
                next_unblock_button(chatId_user)
                bot.send_message(settings.CHAT_ID,'شما کاربر را با موفقیت از حالت بلاک در اوردید!!🙂‍')
                all_button_for_Admin()
                
         
       
@bot.message_handler(func=lambda m: True)
def control_message_Ai_for_user(message):
    chatId = message.chat.id
    text_me = message.text.strip()
    
    # بررسی اگر پیام از ادمین است
    if meessage_checkAdmin(chatId):
        all_button_for_Admin()
        return

    # ۱. بررسی توهین
    ai_toxic = detect_toxicity(text_me.lower())
    if ai_toxic.get("toxic") or ai_toxic.get("score", 0) >= 0.65:
        is_badwordNumber = isBadWordAddDB(chatId)
        bot.send_message(chatId, f"⚠️ پیام نامناسب شناسایی شد. این {is_badwordNumber}‌مین اخطار شماست.")
        if is_badwordNumber >= 5:
            unblock_button(chatId)
            bot.send_message(chatId, "⛔ شما بلاک شدید.")
        return

    # ۲. تشخیص intent
    ai_intent = classify_intent(text_me.lower())
    intent = ai_intent.get("intent")
    confidence = ai_intent.get("confidence", 0)

    # ۳. اگر پیام مرتبط با پروژه یا همکاری است
    if intent in ["project", "contact"] and confidence >= 0.55:
        project_result = groq_process_project(chatId, text_me)

        status = project_result.get("status")
        msg = project_result.get("message", "")

        if status == "complete":
            # ارسال به مدیر
            bot.send_message(settings.CHAT_ID, msg)
            bot.send_message(chatId, "✅ پروژه شما ثبت و برای بررسی به مدیر ارسال شد. ممنون از همکاری شما!")
        elif status == "incomplete":
            # پیام دوستانه به کاربر بدون ذکر پارامترها
            bot.send_message(chatId, msg)
        elif status == "not_my_domain":
            bot.send_message(chatId, msg)
        return

    # ۴. احوالپرسی یا گفتگو دوستانه
    if intent in ["greeting", "spam_or_joke"] and confidence >= 0.6:
        response = groq_chat([
            {"role": "system", "content": "You are a friendly bot that talks naturally but focuses on software/business projects."},
            {"role": "user", "content": text_me}
        ])
        if response:
            bot.send_message(chatId, response)
        else:
            bot.send_message(chatId, "سلام! خوش اومدی 🙂")
        return

    # ۵. fallback برای پیام‌های دیگر
    response_message_normal(message)



        
@bot.message_handler(func=lambda m : True)
def control_message_for_me(text,):

    text_me = text.text.lower()
    chatId= text.chat.id
    is_badwordNumber= 0
    is_qustion = any(listqustion in text_me for listqustion in ['؟','?'])
    is_howAreYou = any(listqustion in text_me for listqustion in howAreyou)
    is_work = any(listqustion in text_me for listqustion in work_list)
    is_freinds = any(listqustion in text_me for listqustion in list_word_friend)
    is_badWord = any(listqustion in text_me for listqustion in list_badword)
    
    admin_check = meessage_checkAdmin(chatId)
    if admin_check:
        all_button_for_Admin()
    else:
            
        is_badwordNumber= isCheckBadWordDB(chatId)
        if is_badWord:
            is_badwordNumber=isBadWordAddDB(chatId)
            
        if is_badwordNumber >=5:
            unblock_button(chatId)
            bot.send_message(chatId, "⛔ شما بلاک شدید. پیام شما پردازش نمی‌شود.")
            
            # blockUser(bot=bot,user_id=text.from_user.id,chat_id=text.chat.id)
            # deleteUser(chat_id=text.chat.id)
        else:
            if is_qustion and is_howAreYou and not is_work:
                bot.send_message(chatId,'!!لطفا احوال پرسی رو بزار کنار و فقط راجب بیزینس با من حرف بزن')
            
            elif is_howAreYou:
                bot.send_message(chatId,'!!لطفا احوال پرسی رو بزار کنار و فقط راجب بیزینس با من حرف بزن')
            elif is_work:
                bot.send_message(chatId,text=f"""
                                پیام شما مهم تشخیص داده شد!!🥹🤍
                                
                                در صورت نیاز میتونید با این شماره تماس بگیرید: {settings.PHONE_ME}

                                اگر کار شما خیلی ضروری نیست و عجله ندارید میتونید به این آیدی پیام بدید: {settings.TELEGRAM_ID_ME}
                                
                                """)
                
            elif is_freinds and not is_badWord:
                bot.send_message(chatId,"""
                                ببین اگه دوست من هستی و میخوای منو خوشحال کنی لطفا فقط از بیزینس صحبت کن!!
                                
                                اگر هم دوست نداری راجب بیزینس باهام حرف بزنی پس بهتره بری سراغ ربات های دیگه

                                ایششششششش😒🙂‍
                                
                                
                                """)
                
            elif is_freinds and  is_badWord:
                bot.send_message(chatId,f"""
                                ببین اگه دوست من هستی و میخوای منو خوشحال کنی لطفا فقط از بیزینس صحبت کن!!
                                
                                اگر هم دوست نداری راجب بیزینس باهام حرف بزنی پس بهتره بری سراغ ربات های دیگه

                                حواسم هم هست که بهم فحش دادی ها تو الان {is_badwordNumber} تعداد اخطار داری اگر به 5 برسه بلاکت میکنما 😒

                                ایششششششش😒🙂‍
                                
                                
                                """)
                
                
            elif not is_freinds and is_badWord:
                if is_badwordNumber>1:
                    bot.send_message(chatId,f"اگر میخوای به فحش دادن من ادامه بدی مجبورم بلاکت کنم\nشما تا الان {is_badwordNumber} اخطار داشته اید\nلطفا دیگه تکرار نکیند!! ")
                
            else:
                response_message_normal(text)


def response_message_normal(message):

    
    selected_response = random.choice(random_text)
    
    bot.send_message(message.chat.id,selected_response)
    


if __name__ == "__main__":
    try:
        print("🤖 Starting bot...")
        bot.polling(
            non_stop=True,
            interval=1,
            timeout=20
        )
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")