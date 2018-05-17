from peewee import *
from entry import *
from tag import *
from database import db

class TagToEntry(Model):
	__tablename__ = 'entrytags'
	
	entry = ForeignKeyField(Entry, backref='tags')
	tag = ForeignKeyField(Tag)
	
	class Meta:
		primary_key = CompositeKey('entry', 'tag')
		database = db