from database import db

from model.entry import Entry
from model.image import Image
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.tag import Tag
from model.tagtoentry import TagToEntry

db.connect()
db.create_tables([Entry, Image, Key, KeyValuePair, Tag, TagToEntry])

test_tag = Tag(name="test")
test_tag.save()

db.close()