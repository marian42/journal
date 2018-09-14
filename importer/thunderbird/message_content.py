from peewee import *
from importer.thunderbird.thunderbird_db import db


class MessageContent(Model):
	docid = IntegerField(primary_key=True)
	c0body = TextField()
	c1subject = TextField()
	c3author = TextField()
	c4recipients = TextField()
	
	class Meta:
		database = db
		db_table = "messagesText_content"
