from database.database import sessionLocale


def get_db():
    """تابع مستقل برای گرفتن session دیتابیس"""
    db = sessionLocale()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_bot():
    from main import bot
    return bot