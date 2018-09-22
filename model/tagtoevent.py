from peewee import *
from .event import *
from .tag import *
from database import db


class TagToEvent(Model):
	__tablename__ = 'entrytags'
	
	event = ForeignKeyField(Event, backref = 'tags', on_delete = 'cascade')
	tag = ForeignKeyField(Tag)
	
	class Meta:
		primary_key = CompositeKey('event', 'tag')
		database = db