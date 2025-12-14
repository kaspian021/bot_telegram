import json, re
from dependense.ai_groq import AIClient
from dependense.const_attributes import work_list
from settings import settings

PROJECT_TEMP = {}
AI = AIClient()  # نمونه async

def detect_project_domain(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["اپ", "application", "app"]):
        return "app"
    if any(word in text_lower for word in work_list):
        return "work"
    if any(word in text_lower for word in ["سایت", "website", "web"]):
        return "website"
    if any(word in text_lower for word in ["بک‌اند", "backend"]):
        return "backend"
    if any(word in text_lower for word in ["ربات"]):
        return "bot"
    if any(word in text_lower for word in ["نرم‌افزار", "software"]):
        return "software"
    if any(word in text_lower for word in ["سخت‌افزار", "hardware"]):
        return "hardware"
    return "other"

def extract_budget(text):
    match = re.search(r'(\d{1,3}(?:[\d,]*)\s*(تومان|ت|T))', text)
    if match:
        return match.group(1)
    return None

def extract_deadline(text):
    match = re.search(r'(\d+\s*(روز|هفته|ماه))', text)
    if match:
        return match.group(1)
    return None

async def groq_process_project(chatId, text):
    """Async پردازش پروژه"""
    if chatId not in PROJECT_TEMP:
        PROJECT_TEMP[chatId] = {"messages": []}
    PROJECT_TEMP[chatId]["messages"].append(text)
    full_text = " ".join(PROJECT_TEMP[chatId]["messages"])

    system_prompt = f"""
You are a professional assistant for software/business projects. 
Determine if user's message contains enough detail.
Allowed domains: {", ".join(settings.MY_SKILLS)}
User messages: {full_text}
"""

    ai_result = await AI.groq_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_text}
    ])

    try:
        result = json.loads(str(ai_result))
    except:
        result = {"status": "incomplete", "message": "پیام شما دریافت شد. لطفاً کمی بیشتر توضیح بده."}

    if result.get("status") == "complete":
        PROJECT_TEMP.pop(chatId, None)

    return result
