from peewee import *

db = SqliteDatabase('journal.db', pragmas = {"foreign_keys": 1})


def init():
	from model.event import Event
	from model.key import Key
	from model.keyvaluepair import KeyValuePair
	from model.tag import Tag
	from model.tagtoevent import TagToEvent
	from model.image import Image
	db.connect()
	db.create_tables([Event, Image, Key, KeyValuePair, Tag, TagToEvent, Image])
	db.close()