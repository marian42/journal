from model.event import Event
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.image import Image
import database as db

db.init()


def add(summary, time, tags = [], kvps = {}, hash = None, latitude = None, longitude = None, images = []):
	result = Event(summary = summary, time = time, latitude = latitude, longitude = longitude, hash = hash)
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
