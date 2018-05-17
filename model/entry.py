from peewee import *

from database import db

class Entry(Model):
	__tablename__ = 'entries'
	
	summary = CharField()
	time = DateTimeField()
	latitude = DoubleField(null=True)
	longitude = DoubleField(null=True)
	hash = CharField(null=True, index=True)
	
	def add_tag(self, tag_name):
		from tag import Tag
		from tagtoentry import TagToEntry
		
		if any(tte.tag.name == tag_name for tte in self.tags):
			return
		
		tag = Tag.get_tag(tag_name)
		tag_to_entry = TagToEntry(tag = tag, entry = self)
		tag_to_entry.save(force_insert=True)
		
	@staticmethod
	def add(summary, time, latitude = None, longitude = None, hash = None, tags = [], kvps = {}):
		result = Entry(summary = summary, time = time, latitude = latitude, longitude = longitude, hash = hash)
		result.save()
		for tag in tags:
			result.add_tag(tag)
		for key in kvps.keys():
			print key
			from key import Key
			from keyvaluepair import KeyValuePair
			db_key = Key.get_key(key)
			kvp = KeyValuePair(key = db_key, value = kvps[key], entry = result)
			kvp.save(force_insert=True)
	
	class Meta:
		database = db