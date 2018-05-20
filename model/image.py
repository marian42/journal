from peewee import *
from event import *
from database import db


class Image(Model):
	__tablename__ = 'images'
	
	event = ForeignKeyField(Event, backref='images')
	file = CharField()
	
	class Meta:
		database = db