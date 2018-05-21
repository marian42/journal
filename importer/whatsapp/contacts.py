from peewee import *

database = SqliteDatabase(None)


class Contact(Model):
	_id = IntegerField(primary_key=True)
	jid = TextField()
	is_whatsapp_user = BooleanField()
	status = TextField()
	number = TextField(null=True)
	display_name = TextField(null=True)
	
	def get_display_name(self):
		if self.display_name is None:
			return ""
		else:
			return self.display_name.encode("utf-8").strip()
	
	class Meta:
		database = database
		db_table = "wa_contacts"