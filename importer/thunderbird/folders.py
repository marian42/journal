from peewee import *
from importer.thunderbird.thunderbird_db import db


class Folder(Model):
	id = IntegerField(primary_key=True)
	folderURI = TextField()
	name = TextField()
	
	class Meta:
		database = db
		db_table = "folderLocations"