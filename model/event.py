from peewee import *
import dateutil.parser
import datetime

from database import db

class Event(Model):
	__tablename__ = 'events'
	
	summary = CharField()
	time = DateTimeField()
	latitude = DoubleField(null=True)
	longitude = DoubleField(null=True)
	hash = CharField(null=True, index=True)
	
	def get_time(self):
		if type(self.time) == datetime.datetime:
			return self.time
		else:
			#return dateutil.parser.parse(self.time)
			result = None
			try:
				result = dateutil.parser.parse(self.time)
			except Exception as e:
				print(e)
				print type(self.time)
				print self.time
			return result
	
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
	
	@staticmethod
	def format_tags(tags, length=25):
		result = tags[0]
		for tag in tags[1:]:
			result += ", " + tag
		if len(result) > length - 2:
			result = "[" + result[:length - 5] + "...]"
		else:
			result = "[" + result + "]" + " " * (length - 2 - len(result))
		return result
	
	def to_string(self):
		return self.get_time().strftime("%Y-%m-%d %H:%M") + " " + Event.format_tags(self.get_tags()) + " " + self.summary
	
	class Meta:
		database = db