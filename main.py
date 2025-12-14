from telebot import TeleBot, apihelper, types
from Buttons.buttons_for_Admin import all_button_for_Admin, button_for_unblock_requestsUser
from dependense.const_attributes import text_information, text_ReadMe, list_word_friend, howAreyou, list_badword, work_list, random_text
from dependense.call_admin import meessage_checkAdmin, message_unBlockForAdmin, message_Admin
from dependense.config import check_block_user, deleteUser, get_All_user, get_All_user_Block, isBadWordAddDB, isRequestsblock, updateUser
from models.users import UserUpdate
from settings import settings
import random
from dependense.orm import get_db
from schemas import users as table
from Buttons.buttons_for_User import next_unblock_button, start_Button, unblock_button
from dependense.tools import groq_process_project
from dependense.ai_groq import AIClient
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
import uvicorn

# ----------------- BOT INIT -----------------
bot = TeleBot(token=settings.TOKEN_BOT, threaded=True)
ai_client = AIClient()  # ⚡ Instance از AIClient

webhook_path = f"/webhook/{settings.TOKEN_BOT}"
webhook_url = f"{settings.SERVER_URL}/botProgrammer{webhook_path}"

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

@app.post(webhook_path)
async def webhook_handler(request: Request):
    try:
        json_data = await request.json()
        update_data = types.Update.de_json(json_data)
        if update_data:
            bot.process_new_updates([update_data])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/botProgrammer")
async def root():
    return {"status": "active", "message": "Bot is running on Render 🚀"}

@app.get("/set_webhook")
async def set_webhook():
    bot.remove_webhook()
    result = bot.set_webhook(url=webhook_url)
    return {"status": "success", "url": webhook_url, "result": result}

@app.get("/remove_webhook")
async def remove_webhook():
    result = bot.remove_webhook()
    return {"status": "success", "result": result}

# ------------------- BOT HANDLERS -------------------

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
                        bot.send_message(chatId, f"سلام خوش برگشتی!\nنام: {message.from_user.first_name}\nتعداد اخطار: {user.isBadWord}")
                    else:
                        new_user = table.Users(
                            chatid=chatId, name=message.from_user.first_name,
                            isBadWord=0, isBlock=False, numberRequestsUnblock=0
                        )
                        db.add(new_user)
                        db.commit()
                        bot.send_message(chatId, f"🙂سلام {message.from_user.first_name} عزیز به ربات خوش آمدید")
                        start_Button(chatId)
            elif message.text == '/help':
                bot.send_message(chatId,'🙂چطور میتونم بهتون کمک کنم؟')
        except apihelper.ApiTelegramException as e:
            if e.error_code == 403:
                deleteUser(chatId)

# ------------------- MESSAGE CONTROL -------------------

@bot.message_handler(func=lambda m: True)
def control_message_for_me(message):
    chatId = message.chat.id
    text_me = message.text.strip()

    # مدیر
    if meessage_checkAdmin(chatId):
        all_button_for_Admin()
        return

    # بلاک
    if check_block_user(chatId):
        bot.send_message(chatId, "⛔ شما بلاک شدید.")
        return

    # بررسی توهین
    ai_toxic = ai_client.detect_toxicity(text_me.lower())
    if ai_toxic.get("toxic") or ai_toxic.get("score",0) >= 0.65:
        warnings = isBadWordAddDB(chatId)
        bot.send_message(chatId, f"⚠️ پیام نامناسب شناسایی شد. این {warnings}‌مین اخطار شماست.")
        if warnings >= 5:
            unblock_button(chatId)
            bot.send_message(chatId, "⛔ شما بلاک شدید.")
        return

    # تشخیص intent
    ai_intent = ai_client.classify_intent(text_me.lower())
    intent = ai_intent.get("intent")
    confidence = ai_intent.get("confidence",0)

    # پروژه یا همکاری
    if intent in ["project", "contact"] and confidence >= 0.55:
        project_result = groq_process_project(chatId, text_me)
        status, msg = project_result.get("status"), project_result.get("message","")
        if status == "complete":
            bot.send_message(settings.CHAT_ID, msg)
            bot.send_message(chatId, "✅ پروژه شما ثبت شد و برای مدیر ارسال شد.")
        else:
            bot.send_message(chatId, msg)
        return

    # احوالپرسی یا پیام دوستانه
    if intent in ["greeting", "spam_or_joke"] and confidence >= 0.6:
        response = ai_client.groq_chat([
            {"role":"system","content":"You are a friendly bot that talks naturally but focuses on software/business projects."},
            {"role":"user","content": text_me}
        ])
        bot.send_message(chatId, response or "سلام! خوش اومدی 🙂")
        return

    # پیام‌های معمولی
    selected_response = random.choice(random_text)
    bot.send_message(chatId, selected_response)

# ------------------- RUN -------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level='info')
