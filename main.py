from database import db

from model.event import Event
from model.image import Image
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.tag import Tag
from model.tagtoentry import TagToEntry
import time

db.connect()
db.create_tables([Event, Image, Key, KeyValuePair, Tag, TagToEntry])

Event.add("summary", time.time(), latitude=42, longitude=43, hash="hashhash", tags=["taga", "tagb"], kvps={"name": "test", "url":"test.com"})

db.close()