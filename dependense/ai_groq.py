import json
import logging
from groq import Groq
from settings import settings
import asyncio

DEFAULT_MODEL = "moonshotai/kimi-k2-instruct-0905"

class AIClient:
    def __init__(self, api_key: str = settings.GROQ_API_KEY):
        self.client = Groq(api_key=api_key)

    @staticmethod
    def safe_strip(text):
        if text and isinstance(text, str):
            return text.strip()
        return ""

    async def groq_chat(self, messages, model=DEFAULT_MODEL, max_tokens=512, temperature=0.0):
        """Async wrapper برای Groq chat completion"""
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            content = resp.choices[0].message.content
            return self.safe_strip(content)
        except Exception:
            logging.exception("Groq request failed")
            return None

    async def classify_intent(self, text: str):
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": (
                            "Classify user message intent. Output JSON only: "
                            '{"intent":"project/contact/greeting/spam_or_joke/other", "confidence":0-1}'
                        )},
                        {"role": "user", "content": text}
                    ],
                    temperature=0
                )
            )
            out = self.safe_strip(resp.choices[0].message.content)
            try:
                return json.loads(out)
            except:
                return {"intent": "other", "confidence": 0.0, "reason": out[:200]}
        except Exception as err:
            return {"intent": "other", "confidence": 0.0, "error": str(err)}

    async def detect_toxicity(self, text: str):
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": (
                            'You are a classifier. Classify message toxicity. Output JSON only: '
                            '{"toxic":bool,"score":0-1}'
                        )},
                        {"role": "user", "content": text}
                    ],
                    temperature=0
                )
            )
            out = self.safe_strip(resp.choices[0].message.content)
            try:
                return json.loads(out)
            except:
                return {"toxic": False, "score": 0.0, "reason": out[:200]}
        except Exception as err:
            return {"toxic": False, "score": 0.0, "error": str(err)}
