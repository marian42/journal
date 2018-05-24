from peewee import *
from thunderbird_db import db
import datetime


class Message(Model):
	id = IntegerField(primary_key=True)
	folderID = IntegerField(null=True)
	conversationID = IntegerField()
	messageKey = IntegerField(null=True)
	date = IntegerField(null=True)
	
	def get_time(self):
		return datetime.datetime.fromtimestamp(self.date / 1000000)
	
	class Meta:
		database = db
		db_table = "messages"