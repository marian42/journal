from database import db


import time

db.connect()
db.create_tables([Event, Image, Key, KeyValuePair, Tag, TagToEntry])
db.close()