from model.event import Event
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.image import Image
import database as db

db.init()


importer_id = 0


def set_importer(id):
	global importer_id
	importer_id = id


def add(summary, time, tags = [], kvps = {}, latitude = None, longitude = None, images = []):
	result = Event(summary = summary, time = time, latitude = latitude, longitude = longitude, importer = importer_id)
	result.save()
	for tag in tags:
		result.add_tag(tag)
	for key in kvps.keys():
		db_key = Key.get_key(key)
		kvp = KeyValuePair(key = db_key, value = kvps[key], event = result)
		kvp.save(force_insert=True)
	for image_time, image_path in images:
		image = Image(event = result, time = image_time, file = image_path)
		image.save()


def clear(id):
	Event.delete().where(Event.importer == id).execute()
	
	
def prepare_import(id):
	set_importer(id)
	clear(id)