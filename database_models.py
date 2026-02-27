from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey,Text
from sqlalchemy.orm import relationship

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    text = Column(Text)
    date = Column(String(255))
    categories = relationship("Category", backref="news")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    news_id = Column(Integer,ForeignKey('news.id'))