from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, func

engine = create_async_engine('postgresql+asyncpg://user:1234@127.0.0.1:5431/netology_aiohttp')
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Adv(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    author = Column(String)


# Base.metadata.create_all()

