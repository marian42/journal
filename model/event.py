from peewee import *

from database import db

class Event(Model):
	__tablename__ = 'events'
	
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
	
	class Meta:
		database = db