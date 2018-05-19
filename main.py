from database import db
from model.event import Event

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
		
def format_tags(tags, length = 25):
	result = tags[0]
	for tag in tags[1:]:
		result += ", " + tag
	if  len(result) > length - 2:
		result = "[" + result[:length - 5] + "...]"
	else:
		result = "[" + result + "]" + " " * (length - 2 - len(result))
	return result

def display_latest():
	query = Event.select().order_by(Event.time)[:100]
	
	for event in query:
		print event.get_time().strftime("%Y-%m-%d %H:%M") + " " + format_tags(event.get_tags()) + " " + event.summary


db.connect()
display_latest()
