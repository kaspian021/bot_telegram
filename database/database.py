from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import settings



SQLURL= settings.SQLURL

engine = create_engine(SQLURL,echo=True,future=True,pool_size=10,
    max_overflow=20,
    pool_pre_ping=True)

sessionLocale = sessionmaker(bind=engine,autoflush=False,autocommit=False,)

Base = declarative_base()