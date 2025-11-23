from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import settings
from sqlalchemy.pool import StaticPool


SQLURL= settings.SQLURL

engine = create_engine(SQLURL,connect_args={'check_same_thread':False},poolclass=StaticPool)

sessionLocale = sessionmaker(bind=engine,autoflush=False,autocommit=False,)

Base = declarative_base()