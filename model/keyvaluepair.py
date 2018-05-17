from peewee import *
from entry import *
from key import *
from database import db

class KeyValuePair(Model):
	__tablename__ = 'keyvaluepairs'
	
	entry = ForeignKeyField(Entry, backref='key_value_pairs')
	key = ForeignKeyField(Key)
	value = CharField()
	
	class Meta:
		primary_key = CompositeKey('entry', 'key')
		database = db