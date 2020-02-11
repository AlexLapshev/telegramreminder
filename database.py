from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from sqlalchemy.pool import StaticPool
engine = create_engine('sqlite:///events.db',
                    connect_args={'check_same_thread':False,
								  'check_same_thread':False},
                    poolclass=StaticPool)


# engine = create_engine('sqlite:///events.db', echo=False, check_same_thread=False)
Base = declarative_base()


class Event(Base):

	__tablename__ = 'events'
	id = Column(Integer, primary_key=True)
	title = Column(String(30))
	date = Column(String(30))

	@staticmethod
	def get_all():
		return session.query(Event).order_by(Event.date).order_by(Event.date).all()

	@staticmethod
	def get_future():
		return session.query(Event).filter(Event.date > datetime.now()).order_by(Event.date).all()

	def __init__(self, title, date):
		self.title = title
		self.date = date

	def __repr__(self):
		return ('Событие: {}, дата: {}.'.format(self.title, self.date))


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()




