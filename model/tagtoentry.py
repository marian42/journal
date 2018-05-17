from peewee import *
from event import *
from tag import *
from database import db

class TagToEntry(Model):
	__tablename__ = 'entrytags'
	
	entry = ForeignKeyField(Event, backref='tags')
	tag = ForeignKeyField(Tag)
	
	class Meta:
		primary_key = CompositeKey('entry', 'tag')
		database = db