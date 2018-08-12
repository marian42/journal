from peewee import *
from .event import *
from .key import *
from database import db


class KeyValuePair(Model):
	__tablename__ = 'keyvaluepair'
	
	event = ForeignKeyField(Event, backref='key_value_pairs')
	key = ForeignKeyField(Key)
	value = CharField()
	
	class Meta:
		primary_key = CompositeKey('event', 'key')
		database = db
