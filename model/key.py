from peewee import *
from database import db

class Key(Model):
	__tablename__ = 'keys'
	
	name = CharField(unique=True)
	
	_items = None
	
	@staticmethod
	def get_key(value):
		if Key._items is None:
			Key._items = {}
			keys = Key.select()
			for key in keys:
				Key._items[key.name] = key
		if value in Key._items:
			return Key._items[value]
		else:
			key = Key(name=value)
			key.save()
			Key._items[value] = key
			return key

	class Meta:
		database = db
