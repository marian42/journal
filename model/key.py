from peewee import *
from database import db

class Key(Model):
	__tablename__ = 'keys'
	
	name = CharField(unique=True)

	class Meta:
		database = db
