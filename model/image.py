from .event import *
from database import db
import os
from PIL import Image as PILImage


class Image(Model):
	__tablename__ = 'images'
	
	event = ForeignKeyField(Event, backref='images')
	file = CharField()
	
	def get_thumbnail_filename(self):
		return "data/thumbnails/" + str(self.id) + "." + self.file.split(".")[-1]
	
	def create_thumbnail(self, skip_if_exists = True):
		filename = self.get_thumbnail_filename()
		if skip_if_exists and os.path.isfile(filename):
			return
		extension = self.file.split(".")[-1].lower()
		format = "JPEG" if extension == "jpg" or extension == "jpeg" else "PNG"
		directory = "/".join(filename.split("/")[0:-1])
		if not os.path.exists(directory):
			os.makedirs(directory)
		
		try:
			image = PILImage.open(self.file)
			image.thumbnail((256, 256), PILImage.ANTIALIAS)
			image.save(filename, format)
		except Exception as e:
			print("Error trying to create thumbnail for " + self.file + ": " + str(e))
	
	class Meta:
		database = db