from peewee import *
from entry import *
from database import db

class Image(Model):
	__tablename__ = 'images'
	
	entry = ForeignKeyField(Entry, backref='tags')
	
	filename = CharField()
	thumbnail_filename = CharField()
	
	class Meta:
		database = db