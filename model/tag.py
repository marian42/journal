from peewee import *
from database import db

class Tag(Model):
	__tablename__ = 'tags'
	
	name = CharField(unique=True)

	class Meta:
		database = db
