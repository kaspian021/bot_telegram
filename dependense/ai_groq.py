# ai_groq.py
import json
import os
from groq import Groq
import logging
from typing import Dict
from settings import settings


client = Groq(api_key=settings.GROQ_API_KEY)


# مدل پیشنهادی: از نسخه 8B یا 70B استفاده کن. 8B برای هزینه/پرفورمنس مناسب‌تره.
DEFAULT_MODEL = "moonshotai/kimi-k2-instruct-0905"  # یا مدل دلخواهی که در Groq داشتی




def groq_chat(messages, model=DEFAULT_MODEL, max_tokens=512, temperature=0.0):
    """
    Wrapper ساده برای chat completion
    messages: list of {"role": "user"/"system"/"assistant", "content": "..." }
    """
    try:
        resp = client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # ساختار پاسخ: resp.choices[0].message.content
        content = resp.choices[0].message.content
        return content
    except Exception as e:
        logging.exception("Groq request failed")
        return None

def classify_intent(text: str):
    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Classify user message intent.
Output JSON only:
{"intent":"project/contact/greeting/spam_or_joke/other", "confidence":0-1}"""
                },
                {"role": "user", "content": text}
            ],
            temperature=0
        )

        # گرفتن محتوا (بدون خطا)
        content = resp.choices[0].message.content
        out = content.strip() if isinstance(content, str) else ""

        try:
            parsed = json.loads(out)
            return parsed
        except Exception:
            return {"intent": "other", "confidence": 0.0, "reason": out[:200]}

    except Exception as err:
        return {"intent": "other", "confidence": 0.0, "error": str(err)}


async def detect_toxicity(text: str):
    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a classifier. Classify message toxicity. Output JSON only: {\"toxic\":bool,\"score\":0-1}"
                },
                {"role": "user", "content": text}
            ],
            temperature=0
        )

        # گرفتن محتوا (بدون خطا)
        content = resp.choices[0].message.content
        out = content.strip() if isinstance(content, str) else ""

        # تبدیل JSON (safe)
        try:
            parsed = json.loads(out)
            return parsed
        except Exception:
            return {"toxic": False, "score": 0.0, "reason": out[:200]}

    except Exception as err:
        return {"toxic": False, "score": 0.0, "error": str(err)}