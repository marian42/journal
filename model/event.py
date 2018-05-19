from peewee import *
import dateutil.parser

from database import db

class Event(Model):
	__tablename__ = 'events'
	
	summary = CharField()
	time = DateTimeField()
	latitude = DoubleField(null=True)
	longitude = DoubleField(null=True)
	hash = CharField(null=True, index=True)
	
	def get_time(self):
		return dateutil.parser.parse(self.time)
	
	def get_tags(self):
		from tagtoevent import TagToEvent
		from tag import Tag
		query = Tag.select(Tag.name)\
			.join(TagToEvent, on=(Tag.id == TagToEvent.tag_id))\
			.where(TagToEvent.event_id == self.id)
		return [tag.name for tag in query]
	
	def add_tag(self, tag_name):
		from tag import Tag
		from tagtoevent import TagToEvent
		
		if any(tte.tag.name == tag_name for tte in self.tags):
			return
		
		tag = Tag.get_tag(tag_name)
		tag_to_event = TagToEvent(tag = tag, event = self)
		tag_to_event.save(force_insert=True)
	
	class Meta:
		database = db