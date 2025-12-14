# ai_groq.py
import json
import logging
from groq import Groq
from settings import settings

DEFAULT_MODEL = "moonshotai/kimi-k2-instruct-0905"  # مدل پیشنهادی


class AIClient:
    def __init__(self, api_key: str = settings.GROQ_API_KEY):
        self.client = Groq(api_key=api_key)

    @staticmethod
    def safe_strip(text):
        """متدی برای جلوگیری از خطای strip روی None"""
        if text and isinstance(text, str):
            return text.strip()
        return ""

    def groq_chat(self, messages, model=DEFAULT_MODEL, max_tokens=512, temperature=0.0):
        """Wrapper برای Groq chat completion"""
        try:
            resp = self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = resp.choices[0].message.content
            return self.safe_strip(content)
        except Exception:
            logging.exception("Groq request failed")
            return None

    def classify_intent(self, text: str):
        """تشخیص نیت پیام کاربر"""
        try:
            resp = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify user message intent. Output JSON only: "
                            '{"intent":"project/contact/greeting/spam_or_joke/other", "confidence":0-1}'
                        )
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0
            )
            content = resp.choices[0].message.content
            out = self.safe_strip(content)
            try:
                return json.loads(out)
            except Exception:
                return {"intent": "other", "confidence": 0.0, "reason": out[:200]}
        except Exception as err:
            return {"intent": "other", "confidence": 0.0, "error": str(err)}

    def detect_toxicity(self, text: str):
        """تشخیص پیام‌های توهین‌آمیز"""
        try:
            resp = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a classifier. Classify message toxicity. "
                            'Output JSON only: {"toxic":bool,"score":0-1}'
                        )
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0
            )
            content = resp.choices[0].message.content
            out = self.safe_strip(content)
            try:
                return json.loads(out)
            except Exception:
                return {"toxic": False, "score": 0.0, "reason": out[:200]}
        except Exception as err:
            return {"toxic": False, "score": 0.0, "error": str(err)}
