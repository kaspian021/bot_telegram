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
    return match.group(1) if match else None

def extract_deadline(text):
    match = re.search(r'(\d+\s*(روز|هفته|ماه))', text)
    return match.group(1) if match else None

async def groq_process_project(chatId, text, user_message):
    """
    پردازش پروژه به صورت async:
    - پیام‌ها رو ذخیره می‌کنه
    - با context قبلی پاسخ میده
    - اگر اطلاعات ناقص باشه، از کاربر می‌پرسه
    - وقتی کامل شد، info پروژه + user برای ادمین آماده می‌کنه
    """
    if chatId not in PROJECT_TEMP:
        PROJECT_TEMP[chatId] = {"messages": []}
    
    PROJECT_TEMP[chatId]["messages"].append(text)
    full_text = " ".join(PROJECT_TEMP[chatId]["messages"])

    system_prompt = f"""
You are a professional assistant for software/business projects.
Check if user provided all required info: 
1. Project type/domain 
2. Budget
3. Deadline/Delivery time
4. Project description/details
If any info is missing, ask the user explicitly.
Use previous messages for context.
Respond in JSON format only:
{{"status":"complete/incomplete", "message_to_user":"", "project_info":{{"type":"", "budget":"", "deadline":"", "description":""}}, "missing_fields":[]}}
User messages: {full_text}
"""

    ai_result = await AI.groq_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_text}
    ])

    try:
        result = json.loads(str(ai_result))
    except:
        result = {
            "status": "incomplete",
            "message_to_user": "پیام شما دریافت شد. لطفاً اطلاعات بیشتری بدهید (بودجه، نوع پروژه، زمان تحویل، توضیحات).",
            "project_info": {"type":"","budget":"","deadline":"","description":""},
            "missing_fields": ["type","budget","deadline","description"]
        }

    # اطمینان از کامل بودن project_info
    project_info = result.get("project_info", {})
    for field in ["type","budget","deadline","description"]:
        project_info.setdefault(field, "")
    result["project_info"] = project_info

    if result.get("status") == "complete":
        # پیام برای ادمین شامل کاربر + پروژه
        result["message_to_admin"] = f"""
📌 پروژه جدید ثبت شد:

👤 کاربر: {user_message}
🆔 ChatID: {chatId}
👤 Username: @{getattr(user_message.from_user,'username','ندارد')}

💼 اطلاعات پروژه:
- نوع پروژه: {project_info.get('type')}
- بودجه: {project_info.get('budget')}
- زمان تحویل: {project_info.get('deadline')}
- توضیحات: {project_info.get('description')}
"""
        # پاک کردن حافظه کاربر برای پروژه بعدی
        PROJECT_TEMP.pop(chatId, None)

    return result
