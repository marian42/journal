import events
from database import db
import os
import datetime
import messages
import contacts
from messages import Message
from contacts import Contact

def get_message_sender(message, contacts_dict):
	if message.remote_resource != None and contacts_dict.has_key(message.remote_resource):
		return contacts_dict[message.remote_resource].get_display_name()
	elif message.key_from_me == 1:
		return "Me"
	else:
		return contacts_dict[message.key_remote_jid].get_display_name()
	
def log_image(directory, message, contact):
	filename = directory + "Media/WhatsApp Images/" + ("Sent/" if message.is_sent() else "") + message.media_name
	time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
	
	if os.path.isfile(filename):
		summary = ("Sent" if message.is_sent() else "Received") + " an image " + ("to" if message.is_sent() else "from") + " " \
		          + contact.get_display_name() \
		          + (": " + message.media_caption.encode("utf-8") if message.media_caption is not None else ".")
		events.add(summary, time, ["whatsapp", "message", "image"],
		           {"message": message.media_caption.encode("utf-8")} if message.media_caption is not None else {},
		           "wa-" + str(message._id), images=[filename])


def log_location(message, contact):
	time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
	
	summary = ("Sent" if message.is_sent() else "Received") + " location " + (
		"to" if message.is_sent() else "from") + " " \
	          + contact.get_display_name() \
	          + (": " + message.media_caption.encode("utf-8") if message.media_caption is not None else ".")
	events.add(summary, time, ["whatsapp", "message", "location"],
	           {"message": message.media_name.encode("utf-8")} if message.media_name is not None else {},
	           "wa-" + str(message._id), latitude=message.latitude, longitude=message.longitude)


def create_conversation_event(contact, message_count, time, history, first):
	kvps = {"message": history}
	if first:
		events.add(
			"Started a Whatsapp conversation with " + contact.get_display_name() + " (" + str(message_count) + " message" + ("s" if message_count > 1 else "") + ").",
			time, ["whatsapp", "message"], kvps)
	else:
		events.add(
			"Exchanged " + str(message_count) + " Whatsapp message" + (
				"s" if message_count > 1 else "") + " with " + contact.get_display_name() + ".",
			time, ["whatsapp", "message"], kvps)

def read_conversation(directory, contact_jid, contacts_dict):
	contact = contacts_dict[contact_jid]
	query = Message.select().where(Message.timestamp != 0 and Message.key_remote_jid == contact_jid).order_by(
		Message.timestamp)
	
	session_start_time = None
	last_message_time = None
	history = ""
	message_count = 0
	session_count = 0

	for message in query:
		sender = get_message_sender(message, contacts_dict)
		message_time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
		
		# TODO doesn't work with received images
		if message.media_name is not None:
			log_image(directory, message, contact)
		
		if message.latitude != 0 and message.longitude != 0:
			log_location(message, contact)
		
		if session_start_time is None:
			session_start_time = message_time
		elif (message_time - last_message_time).total_seconds() > 4 * 60 * 60:
			create_conversation_event(contact, message_count, session_start_time, history, session_count == 0)
			
			session_start_time = message_time
			message_count = 0
			session_count += 1
			history = ""
		last_message_time = message_time
		message_count += 1
		history += sender + ": " + message.get_text() + "\n"
	
	if message_count > 0:
		create_conversation_event(contact, message_count, session_start_time, history, session_count == 0)
			
def get_contacts_dict(directory):
	contacts.database.init(directory + "wa.db")
	contacts_dict = {}
	
	query = Contact.select()
	for contact in query:
		contacts_dict[contact.jid] = contact
		
	return contacts_dict

def import_whatsapp(directory="data/WhatsApp/"):
	messages.database.init(directory + "msgstore.db")
	
	contacts_dict = get_contacts_dict(directory)
	
	with db.atomic():
		for contact_jid in contacts_dict.keys():
			read_conversation(directory, contact_jid, contacts_dict)

if __name__ == "__main__":
	import_whatsapp()