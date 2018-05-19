from database import db
from model.event import Event
import events

def remove_duplicates():
	Event2 = Event.alias()
	query = Event.select(Event.id)\
		.join(Event2, on=(Event.hash == Event2.hash))\
		.where(Event.hash.is_null(False) and Event.id > Event2.id)
	
	with db.atomic():
		print "Deleting " + str(len(query)) + " duplicates..."
		for item in query:
			Event.delete_by_id(item.id)
		print "Done."
		


def display_latest():
	query = Event.select().order_by(Event.time)[:100]
	
	for event in query:
		print event.to_string()


db.connect()
display_latest()
