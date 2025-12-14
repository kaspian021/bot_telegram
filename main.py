import asyncio
from telebot import TeleBot, apihelper, types
from Buttons.buttons_for_Admin import all_button_for_Admin, button_for_unblock_requestsUser
from dependense.const_attributes import text_information, text_ReadMe, list_word_friend, howAreyou, list_badword, work_list, random_text
from dependense.call_admin import meessage_checkAdmin, message_unBlockForAdmin, message_Admin
from dependense.config import check_block_user, deleteUser, get_All_user, get_All_user_Block, isBadWordAddDB, isCheckBadWordDB, isRequestsblock, updateUser
from models.users import UserCreate, UserUpdate
from settings import settings
import random
from dependense.orm import get_db
from schemas import users as table
from Buttons.buttons_for_User import next_unblock_button, start_Button, unblock_button
from dependense.ai_groq import AIClient
from dependense.tools import detect_project_domain, groq_process_project
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from database.database import Base, engine

bot = TeleBot(token=settings.TOKEN_BOT, threaded=True)
AI = AIClient()  # نمونه async هوش مصنوعی
baseUrlBot = '/botProgrammer'
# Webhook URL
webhook_path = f"/webhook/{settings.TOKEN_BOT}"
webhook_url = f"{settings.SERVER_URL}{baseUrlBot}{webhook_path}"

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
    description='ربات دستیار برنامه نویس',
    version='1.0.0',
    lifespan=lifespan,
)

@app.post(f'{baseUrlBot}{webhook_path}')
async def webhook_handler(request: Request):
    try:
        json_data = await request.json()
        update_data = types.Update.de_json(json_data)
        if update_data:
            bot.process_new_updates([update_data])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get(baseUrlBot)
async def root():
    return {"status": "active", "message": "Bot is running on Render 🚀"}

@app.get(f"{baseUrlBot}/set_webhook")
async def set_webhook():
    bot.remove_webhook()
    result = bot.set_webhook(url=webhook_url)
    return {"status": "success", "url": webhook_url, "result": result}

@app.get(f"{baseUrlBot}/remove_webhook")
async def remove_webhook():
    result = bot.remove_webhook()
    return {"status": "success", "result": result}

# ---------------- BOT COMMANDS ----------------
@bot.message_handler(commands=['start','help'])
def start_bot(message):
    chatId = message.chat.id
    with get_db() as db:
        try:
            if message.text == '/start':
                if meessage_checkAdmin(chatId):
                    message_Admin('سلام رئیس خوش اومدی به ربات خودت🙂‍')
                else:
                    user = db.query(table.Users).filter(table.Users.chatid==chatId).first()
                    if user:
                        bot.send_message(chatId, f"سلام خوش برگشتی به ربات شخصی (Alikaspian)\nاطلاعات شما:\nنام: {message.from_user.first_name}\nتعداد اخطار: {user.isBadWord}")
                    else:
                        new_user = table.Users(
                            chatid=chatId,
                            name=message.from_user.first_name,
                            isBadWord=0,
                            isBlock=False,
                            numberRequestsUnblock=0
                        )
                        db.add(new_user)
                        db.commit()
                        bot.send_message(chatId, f"🙂سلام {message.from_user.first_name} عزیز به ربات همکاری و شخصی (Alikaspian) خوش آمدید")
                        start_Button(chatId)
            elif message.text == '/help':
                bot.send_message(chatId,'🙂چطور میتونم بهتون کمک کنم؟')
        except apihelper.ApiTelegramException as e:
            if e.error_code == 403:
                deleteUser(chatId)
            else:
                raise e

# ---------------- ADMIN HANDLERS ----------------
@bot.message_handler(commands=['AllUser','AllUserBlock'])
def admin_message_handler(m):
    chatId = m.chat.id
    if not meessage_checkAdmin(chatId):
        bot.send_message(chatId, "⚠️ شما دسترسی ادمین ندارید.")
        return

    text = m.text
    if text == '/AllUser':
        result = get_All_user()
        if result and result.all_user:
            message_text = "👥 <b>لیست تمام کاربران</b>\n\n"
            message_text += "┌───────────────┬─────────────────┬──────────────┬────────────────┐\n"
            message_text += "│<b>ردیف</b>│ <b>نام</b>   │   <b>بلاک</b>    │  <b>کلمات بد</b> │\n"
            message_text += "├───────────────┼─────────────────┼──────────────┼────────────────┤\n"
            for i, user in enumerate(result.all_user, 1):
                name = user.name if len(user.name) <= 8 else user.name[:7] + "…"
                block_icon = "🔴" if user.isBlock else "🟢"
                badword_icon = user.isBadWord
                message_text += f"│  {i:2d}  │ {name:10} │   {block_icon}    │    {badword_icon}     │\n"
            message_text += "└───────┴────────────┴──────────┴────────────┘\n"
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

# ---------------- USER BUTTONS ----------------
@bot.message_handler(commands=['unblock','information','about'])
def message_All_Button(m):
    chat_id = m.chat.id
    with get_db() as db:
        if meessage_checkAdmin(chat_id):
            all_button_for_Admin()
            return

        user = db.query(table.Users).filter(table.Users.chatid==chat_id).first()
        if not user:
            return

        if m.text == '/unblock':
            if not check_block_user(chat_id):
                bot.send_message(chat_id,'شما بلاک نشده‌اید بنابراین نمیتوانید از این دستور استفاده کنید🙂')
                return
            if not isRequestsblock(chat_id):
                bot.send_message(chat_id,'شما قبلا درخواست داده‌اید، لطفا منتظر نتیجه بمانید!!')
                return
            message_unBlockForAdmin(userName=str(user.name), chat_id=chat_id)
            updateUser(chat_id=chat_id, data=UserUpdate(numberRequestsUnblock=1))
            button_for_unblock_requestsUser(chat_id)
            bot.send_message(chat_id,'درخواست آنبلاک برای ادمین ارسال شد، لطفا منتظر پاسخ باشید!!😒')
        elif m.text == '/information':
            bot.send_message(chat_id, text=text_information, parse_mode='HTML')
        elif m.text == '/about':
            bot.send_message(chat_id, text=text_ReadMe, parse_mode='HTML')

# ---------------- ADMIN UNBLOCK HANDLER ----------------
@bot.message_handler(regexp=r"^/unblock:\d{1,15}$")
def message_All_Admin(m):
    chatId = m.chat.id
    if settings.CHAT_ID != chatId:
        return

    resulttext = m.text.split(':')
    chatId_user = int(resulttext[1])
    updateUser(chat_id=chatId_user, data=UserUpdate(isBadWord=0, isBlock=False, numberRequestsUnblock=0))
    bot.send_message(chatId_user,'ادمین شمارا از بلاک درآورد، تبریک می‌گویم 🙂‍')
    next_unblock_button(chatId_user)
    bot.send_message(settings.CHAT_ID,'کاربر با موفقیت آنبلاک شد!')
    all_button_for_Admin()

# ---------------- MESSAGE HANDLER ----------------
@bot.message_handler(func=lambda m: True)
def control_message_for_me(message):
    chatId = message.chat.id
    text_me = message.text.strip()
    bot.send_chat_action(chatId, 'typing')

    async def process_message():
        if meessage_checkAdmin(chatId):
            all_button_for_Admin()
            return
        if check_block_user(chatId):
            bot.send_message(chatId, "⛔ شما بلاک شدید.")
            return

        ai_toxic = await AI.detect_toxicity(text_me.lower())
        if ai_toxic.get("toxic") or ai_toxic.get("score",0)>=0.65:
            warnings = isBadWordAddDB(chatId)
            bot.send_message(chatId,f"⚠️ پیام نامناسب شناسایی شد. این {warnings}‌مین اخطار شماست.")
            if warnings>=5:
                updateUser(chat_id=chatId,data=UserUpdate(isBlock=True))
                unblock_button(chatId)
                bot.send_message(chatId,"⛔ شما بلاک شدید.")
            return

        ai_intent = await AI.classify_intent(text_me.lower())
        intent = ai_intent.get("intent")
        confidence = ai_intent.get("confidence",0)

        if intent in ["project","contact"] and confidence>=0.55:
            project_result = await groq_process_project(chatId,text_me)
            status, msg = project_result.get("status"), project_result.get("message","")
            if status=="complete":
                bot.send_message(settings.CHAT_ID,msg)
                bot.send_message(chatId,"✅ پروژه شما ثبت شد و برای مدیر ارسال شد.")
            else:
                bot.send_message(chatId,msg)
            return

        if intent in ["greeting","spam_or_joke"] and confidence>=0.6:
            response = await AI.groq_chat([
                {"role":"system","content":"You are a friendly bot..."},
                {"role":"user","content":text_me}
            ])
            bot.send_message(chatId,response or "سلام! خوش اومدی 🙂")
            return

        bot.send_message(chatId, random.choice(random_text))

    asyncio.run(process_message())

# ---------------- RUN ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level='info')
