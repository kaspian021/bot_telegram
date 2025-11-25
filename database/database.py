from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import settings



SQLURL= settings.SQLURL

engine = create_engine(SQLURL,echo=True,future=True)

sessionLocale = sessionmaker(bind=engine,autoflush=False,autocommit=False,)

Base = declarative_base()