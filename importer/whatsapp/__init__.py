import events
from database import db
import os
import datetime
import importer.whatsapp.messages as messages
import importer.whatsapp.contacts as contacts
from importer.whatsapp.messages import Message
from importer.whatsapp.contacts import Contact


def get_message_sender(message, contacts_dict):
	if message.remote_resource is not None and message.remote_resource in contacts_dict:
		return contacts_dict[message.remote_resource].get_display_name(), False
	elif message.key_from_me == 1:
		return "Me", True
	else:
		return contacts_dict[message.key_remote_jid].get_display_name(), False


def log_location(message, contact):
	time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
	
	summary = ("Sent" if message.is_sent() else "Received") + " location " + (
		"to" if message.is_sent() else "from") + " " \
			+ contact.get_display_name() \
			+ (": " + message.media_caption.encode("utf-8") if message.media_caption is not None else ".")
	events.add(summary, time, ["whatsapp", "message", "location"],
			{"message": message.media_name.encode("utf-8")} if message.media_name is not None else {}, latitude=message.latitude, longitude=message.longitude)


def create_conversation_event(contact, message_count, time, history, images, sent_any, received_any):
	kvps = {"message": history}
	tags = ["whatsapp", "message"]
	if len(images) != 0:
		tags.append("photo")
	
	summary = "Exchanged" if sent_any and received_any else ("Sent" if sent_any else "Received")
	summary += " "
	summary += "a message" if message_count == 1 else (str(message_count) + " messages")
	summary += " "
	summary += "with" if sent_any and received_any else ("to" if sent_any else "from")
	summary += " " + contact.get_display_name() + "."
	
	events.add(summary, time, tags, kvps, images = images)


def read_conversation(directory, contact_jid, contacts_dict):
	contact = contacts_dict[contact_jid]
	print("Reading Whatsapp conversation with " + contact.get_display_name() + "...")
	query = Message.select().where(Message.timestamp != 0 and Message.key_remote_jid == contact_jid).order_by(Message.timestamp)
	
	session_start_time = None
	last_message_time = None
	history = ""
	images = []
	message_count = 0
	sent_any = False
	received_any = False

	for message in query:
		sender, sent = get_message_sender(message, contacts_dict)
		message_time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
		
		# TODO doesn't work with received images
		if message.media_name is not None:
			filename = directory + "Media/WhatsApp Images/" + ("Sent/" if message.is_sent() else "") + message.media_name
			time = datetime.datetime.fromtimestamp(message.timestamp / 1000)
			if os.path.isfile(filename):
				images.append((time, filename))
		
		if message.latitude != 0 and message.longitude != 0:
			log_location(message, contact)
		
		if session_start_time is None:
			session_start_time = message_time
		elif (message_time - last_message_time).total_seconds() > 4 * 60 * 60:
			create_conversation_event(contact, message_count, session_start_time, history, images, sent_any, received_any)
			
			session_start_time = message_time
			message_count = 0
			history = ""
			images = []
			sent_any = False
			received_any = False
		
		if sent:
			sent_any = True
		else:
			received_any = True
		last_message_time = message_time
		message_count += 1
		history += sender + ": " + message.get_text() + "\n"
	
	if message_count > 0:
		create_conversation_event(contact, message_count, session_start_time, history, images, sent_any, received_any)


def get_contacts_dict(directory):
	contacts.database.init(directory + "wa.db")
	contacts_dict = {}
	
	query = Contact.select()
	for contact in query:
		contacts_dict[contact.jid] = contact
		
	return contacts_dict


def import_whatsapp(directory="data/WhatsApp/"):
	events.prepare_import(12)
	
	messages.database.init(directory + "msgstore.db")
	
	contacts_dict = get_contacts_dict(directory)
	
	print("Reading Whatsapp conversations...")
	
	with db.atomic():
		for contact_jid in contacts_dict.keys():
			read_conversation(directory, contact_jid, contacts_dict)
	print("Done.")


if __name__ == "__main__":
	import_whatsapp()
