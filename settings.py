from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    TOKEN_BOT:str = os.getenv('TOKEN_BOT','')
    PHONE_ME:str = os.getenv('PHONE_ME','')
    TELEGRAM_ID_ME:str = os.getenv('TELEGRAM_ID_ME','')
    SQLURL:str = os.getenv('SQLURL','')
    CHAT_ID:int = int(os.getenv('CHAT_ID',0))
    GROQ_API_KEY:str = os.getenv("GROQ_API_KEY",'')
    ENVIRONMENT:str = os.getenv("ENVIRONMENT",'')
    APP_NAME:str = os.getenv("APP_NAME",'')
    MY_SKILLS:list = list(os.getenv("MY_SKILLS",[]))
    class Config:
        env_file= '.env'
        
        

settings= Settings()