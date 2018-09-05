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
			result = None
			try:
				result = dateutil.parser.parse(self.time)
			except Exception as e:
				print(e)
				print(type(self.time))
				print(self.time)
			return result
	
	def get_tags(self):
		from model.tagtoevent import TagToEvent
		from model.tag import Tag
		query = Tag.select(Tag.name)\
			.join(TagToEvent, on=(Tag.id == TagToEvent.tag_id))\
			.where(TagToEvent.event_id == self.id)
		return [tag.name for tag in query]
	
	def add_tag(self, tag_name):
		from model.tag import Tag
		from model.tagtoevent import TagToEvent
		
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
	
	def get_value(self, key):
		from model.key import Key
		from model.keyvaluepair import KeyValuePair
		
		try:
			return KeyValuePair.get((KeyValuePair.key == Key.get_key(key)) & (KeyValuePair.event == self)).value
		except DoesNotExist:
			return None
	
	def to_string(self):
		return self.get_time().strftime("%Y-%m-%d %H:%M") + " " + Event.format_tags(self.get_tags()) + " " + self.summary
	
	class Meta:
		database = db