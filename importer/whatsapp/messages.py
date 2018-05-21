from peewee import *

database = SqliteDatabase(None)

media_types = {
	"image": "Image",
	"video": "Video",
	"audio": "Voice message",
	"application": "PDF"
}

class Message(Model):
	_id = IntegerField(primary_key=True)
	key_remote_jid = TextField()
	key_from_me = IntegerField()
	key_id = TextField()
	status = IntegerField()
	data = TextField(null=True)
	timestamp = IntegerField()
	media_name = TextField()
	media_caption = TextField()
	media_mime_type = TextField()
	remote_resource = TextField(null=True)
	latitude = DoubleField(null=True)
	longitude = DoubleField(null=True)
	
	def get_text(self):
		if self.media_caption is not None:
			return self.media_caption.encode("utf-8")
		elif self.data is not None:
			return self.data.encode("utf-8")
		elif self.media_mime_type is not None:
			type = self.media_mime_type.split("/")[0]
			return media_types[type]
		else:
			return ""
	
	def is_sent(self):
		return self.key_from_me == 1
	
	class Meta:
		database = database
		db_table = "messages"