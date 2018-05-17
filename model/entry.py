from peewee import *

from database import db

class Entry(Model):
	__tablename__ = 'entries'
	
	id = BigIntegerField(primary_key=True)
	summary = CharField()
	time = DateTimeField()
	latitude = DoubleField(null=True)
	longitude = DoubleField(null=True)
	
	class Meta:
		database = db