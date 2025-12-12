
import asyncio
from telebot import TeleBot,apihelper,types
from Buttons.buttons_for_Admin import all_button_for_Admin, button_for_unblock_requestsUser
from dependense.const_attributes import text_information,text_ReadMe,list_word_friend,howAreyou,list_badword,work_list,random_text
from dependense.call_admin import meessage_checkAdmin, message_unBlockForAdmin, message_Admin
from dependense.config import check_block_user, deleteUser, get_All_user, get_All_user_Block, isBadWordAddDB, isCheckBadWordDB, isRequestsblock, updateUser
from models.users import UserCreate, UserUpdate
from settings import settings
import random
from dependense.orm import get_db
from schemas import users as table
from Buttons.buttons_for_User import next_unblock_button, start_Button, unblock_button
from dependense.ai_groq import classify_intent, detect_toxicity, groq_chat
from dependense.tools import detect_project_domain, groq_process_project
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request,HTTPException
import uvicorn
from database.database import Base,engine




bot = TeleBot(token=settings.TOKEN_BOT, threaded=True)


# Webhook URL Render (در محیط Render تنظیم می‌شود)
webhook_path = f"/webhook/{settings.TOKEN_BOT}"
webhook_url = f"{settings.SERVER_URL}{webhook_path}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "production":
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")

    yield

    bot.remove_webhook()
    print("Webhook removed.")



app = FastAPI(
    title='Telegram Bot Api',
    description='ربات دستیار برنامه نویس - نسخه Render',
    version='1.0.0',
    lifespan=lifespan
)





@app.post(webhook_path)
async def webhook_handler(request: Request):
    try:
        json_data = await request.json()
        update_data = types.Update.de_json(json_data)
        if update_data:
            bot.process_new_updates([update_data])
            print('Update processed')
        return {"status": "ok"}
    except Exception as e:
        print(f"Error webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {
        "status": "active",
        "message": "Bot is running on Render 🚀"
    }


@app.get("/set_webhook")
async def set_webhook():
    try:
        bot.remove_webhook()
        result = bot.set_webhook(url=webhook_url)
        return {"status": "success", "url": webhook_url, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/remove_webhook")
async def remove_webhook():
    try:
        result = bot.remove_webhook()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
                        numberRequestsUnblock=0
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
                    result_number_requests= isRequestsblock(chat_id)
                    if not result_number_requests:
                        bot.send_message(chat_id,'شما یه بار درخواست ارسال کرده اید لطفا منتظر نتیجه بمانید!!')
                        return
                        
                    result_btn1= message_unBlockForAdmin(userName=str(result.name),chat_id=chat_id)
                    if result_btn1:
                        resultUpdate= updateUser(chat_id=chat_id,data=UserUpdate(numberRequestsUnblock=1))
                        if resultUpdate:
                            
                            button_for_unblock_requestsUser(chat_id)
                            bot.send_message(chat_id,'درخواست آنبلاک برای ادمین با موفقیت ارسال شد منتظر نتیجه بمانید!!😒')
                        else:
                            bot.send_message(chat_id,'خطایی پیش امد لطفا دوباره امتحان کنید!!')
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
            
            resulttext = textAdmin.split(':')
            chatId_user= int(resulttext[1])
            result= updateUser(chat_id=chatId_user,data=UserUpdate(isBadWord=0,isBlock=False,numberRequestsUnblock=0))
            
            if result:
                bot.send_message(chatId_user,'ادمین بررسی کرد و شمارو از بلاکی در اورد\nتبریک میگم شما دوباره میتونید راجب پروژه و بیزینس با من حرف بزنی🙂‍')
                next_unblock_button(chatId_user)
                bot.send_message(settings.CHAT_ID,'شما کاربر را با موفقیت از حالت بلاک در اوردید!!🙂‍')
                all_button_for_Admin()
                
         
       





async def process_message(text_obj):
    chatId = text_obj.chat.id
    text_me = text_obj.text.strip()

    # اگر پیام از ادمین است
    if meessage_checkAdmin(chatId):
        all_button_for_Admin()
        return

    # بررسی بلاک بودن
    if check_block_user(chatId):
        bot.send_message(chatId, "⛔ شما بلاک شدید.")
        return

    # ---------------------------
    # 1️⃣ بررسی توهین
    ai_toxic = await detect_toxicity(text_me.lower())
    if ai_toxic.get("toxic") or ai_toxic.get("score", 0) >= 0.65:
        
        isbad = isBadWordAddDB(chatId)
        bot.send_message(chatId, f"⚠️ پیام نامناسب شناسایی شد. این {isbad}‌مین اخطار شماست.")
        if isbad >= 5:
            unblock_button(chatId)
            bot.send_message(chatId, "⛔ شما بلاک شدید.")
        return

    # ---------------------------
    # 2️⃣ تشخیص intent
    ai_intent = await classify_intent(text_me.lower())
    intent = ai_intent.get("intent")
    confidence = ai_intent.get("confidence", 0)

    if intent in ["project", "contact"] and confidence >= 0.55:
        project_result = await groq_process_project(chatId, text_me)
        msg = project_result.get("message", "")
        if project_result.get("status") == "complete":
            bot.send_message(settings.CHAT_ID, msg)
            bot.send_message(chatId, "✅ پروژه شما ثبت و برای بررسی به مدیر ارسال شد. ممنون از همکاری شما!")
        else:
            bot.send_message(chatId, msg)
        return

    # ---------------------------
    # 3️⃣ احوالپرسی یا گفتگو دوستانه
    if intent in ["greeting", "spam_or_joke"] and confidence >= 0.6:
        response = await groq_chat([
            {"role": "system", "content": "You are a friendly bot that talks naturally but focuses on software/business projects."},
            {"role": "user", "content": text_me}
        ], max_tokens=128)
        bot.send_message(chatId, response or "سلام! خوش اومدی 🙂")
        return

    # ---------------------------
    # پیام‌های معمولی / قواعد شخصی
    await handle_custom_responses(chatId, text_me)


async def handle_custom_responses(chatId, text_me):
    # نمونه قوانین شخصی و پاسخ سریع
    is_work = any(word in text_me for word in ["پروژه", "کار", "task"])
    is_freinds = any(word in text_me for word in ["دوست", "رفیق"])
    is_badWord = any(word in text_me for word in ["فحش", "لعنت"])
    
    if is_work:
        bot.send_message(chatId, f"پیام شما مهم تشخیص داده شد!!\nدر صورت نیاز میتونید با این شماره تماس بگیرید: {settings.PHONE_ME}")
    elif is_freinds and not is_badWord:
        bot.send_message(chatId, "لطفا فقط از بیزینس صحبت کن!!")
    elif is_badWord:
        bot.send_message(chatId, "⚠️ لطفا از کلمات بد استفاده نکنید!")
    else:
        bot.send_message(chatId, random.choice(["پیام دریافت شد 🙂", "در حال بررسی پیام شما...", "ممنون! پیام شما ثبت شد."]))


# ---------------------------
# Wrapper برای TeleBot (sync -> async)
@bot.message_handler(func=lambda m: True)
def control_message_for_me_wrapper(message):
    asyncio.run(process_message(message))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level='info'
    )