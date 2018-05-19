from peewee import *

db = SqliteDatabase('journal.db')

def init():
	from model.event import Event
	from model.image import Image
	from model.key import Key
	from model.keyvaluepair import KeyValuePair
	from model.tag import Tag
	from model.tagtoevent import TagToEvent
	db.connect()
	db.create_tables([Event, Image, Key, KeyValuePair, Tag, TagToEvent])
	db.close()