from model.event import Event
from model.key import Key
from model.keyvaluepair import KeyValuePair
import database as db

db.init()

def add(summary, time, latitude = None, longitude = None, hash = None, tags = [], kvps = {}):
	result = Event(summary = summary, time = time, latitude = latitude, longitude = longitude, hash = hash)
	result.save()
	for tag in tags:
		result.add_tag(tag)
	for key in kvps.keys():
		db_key = Key.get_key(key)
		kvp = KeyValuePair(key = db_key, value = kvps[key], entry = result)
		kvp.save(force_insert=True)