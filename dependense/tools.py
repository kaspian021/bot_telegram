import json
import re
from settings import settings
from dependense.const_attributes import work_list
from dependense.ai_groq import AIClient

PROJECT_TEMP = {}

ai_client = AIClient()  # ⚡ فقط یکبار شی ساخته میشه و استفاده میشه

def detect_project_domain(text: str) -> str:
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

def extract_budget(text: str):
    """تشخیص بودجه به تومان یا عدد"""
    match = re.search(r'(\d{1,3}(?:[\d,]*)\s*(تومان|ت|T))', text)
    if match:
        return match.group(1)
    return None

def extract_deadline(text: str):
    """تشخیص زمان‌بندی با کلمات هفته، ماه، روز"""
    match = re.search(r'(\d+\s*(روز|هفته|ماه))', text)
    if match:
        return match.group(1)
    return None

def groq_process_project(chatId: int, text: str) -> dict:
    """
    پردازش پروژه با کمک AI:
    - بررسی کامل بودن توضیحات پروژه
    - استخراج خودکار type, description, deadline, budget
    - آماده‌سازی پیام نهایی برای مدیر
    """
    if chatId not in PROJECT_TEMP:
        PROJECT_TEMP[chatId] = {"messages": []}

    PROJECT_TEMP[chatId]["messages"].append(text)
    full_text = " ".join(PROJECT_TEMP[chatId]["messages"])

    system_prompt = f"""
You are a professional assistant for software/business projects. 
1. Determine if the user's messages contain enough detail for a project.
2. If complete, return JSON:
{{"status": "complete", "message": "formatted message for admin", "data": {{"type": "...", "description": "...", "deadline": "...", "budget": "..."}}}} 
3. If incomplete, return JSON:
{{"status": "incomplete", "message": "friendly message asking user to explain more"}}
4. If outside allowed domains, return JSON:
{{"status": "not_my_domain", "message": "متاسفم، این حوزه کاری من نیست."}}
Allowed domains: {", ".join(settings.MY_SKILLS)}
User messages: {full_text}
"""

    # ⚡ استفاده صحیح از instance
    ai_result = ai_client.groq_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_text}
    ])

    # اگر پاسخ None یا خطا بود fallback
    try:
        result = json.loads(ai_result) if ai_result else {}
    except Exception:
        result = {
            "status": "incomplete",
            "message": "پیام شما دریافت شد. لطفاً کمی بیشتر توضیح بده تا بتوانم پروژه را کامل ثبت کنم."
        }

    # اگر پروژه کامل شد → پاک کردن موقت
    if result.get("status") == "complete":
        PROJECT_TEMP.pop(chatId, None)

    return result
