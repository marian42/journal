from peewee import *
import thunderbird_db
from folders import Folder
from message import Message
from message_content import MessageContent
import events
from database import db

def get_short_recipients(value):
	result = []
	name = None
	mail = None
	for block in value.split(","):
		for word in block.strip().split(" "):
			if mail is not None:
				continue
			if len(word) == 0:
				continue
			word = word.strip()
			if word[0] == '"':
				word = word[1:]
			if word[-1] == '"':
				word = word[:-1]
			if "@" in word:
				if word[0] == '<':
					word = word[1:]
				if word[-1] == '>':
					word = word[:-1]
				mail = word
			elif name is None:
				name = word
			else:
				name += " " + word
		if mail is not None:
			if name is not None:
				result.append(name)
			else:
				result.append(mail)
			mail = None
			name = None
		elif name is not None:
			name += ","
	if len(result) == 0:
		return ""
	elif len(result) == 1:
		return result[0]
	else:
		return ", ".join(result[:-1]) + " and " + result[-1]

def get_folder_ids():
	sent_folder_names = ["sent", "gesendet"]
	
	ids = []
	
	for folder in Folder.select():
		if folder.name.lower() in sent_folder_names:
			ids.append(folder.id)
			
	return ids

def read_messages(query, replies):
	tags = ["email"] + (["reply"] if replies else [])
	for item in query:
		time = item.get_time()
		author = item.content.c3author
		subject = ("Re: " if replies else "") + item.content.c1subject
		body = item.content.c0body
		recipients = item.content.c4recipients
		kvps = {"author": author, "subject": subject, "recipients": recipients, "message": "" if body is None else body}
		summary = ("Replied to " if replies else "Sent an email to ") + get_short_recipients(recipients) + ": " + subject
		
		events.add(summary, time, tags, kvps, "mail-" + str(item.id))

def import_thunderbird(directory="data/thunderbird/"):
	thunderbird_db.db.init(directory + "global-messages-db.sqlite")
	
	with db.atomic():
		folder_ids = get_folder_ids()
		
		Message2 = Message.alias()
		query = Message.select(Message.folderID, Message.date, MessageContent.c1subject, MessageContent.c0body, MessageContent.c3author, MessageContent.c4recipients)\
			.join(MessageContent, on = (Message.id == MessageContent.docid).alias("content"))\
			.where(Message.folderID << folder_ids & ~fn.EXISTS(Message2.select().where((Message.date > Message2.date) & (Message.conversationID == Message2.conversationID))))\
			.order_by(Message.date)
		
		read_messages(query, False)
		
		query = Message.select(Message.folderID, Message.date, MessageContent.c1subject, MessageContent.c0body, MessageContent.c3author, MessageContent.c4recipients) \
			.join(MessageContent, on=(Message.id == MessageContent.docid).alias("content")) \
			.where(Message.folderID << folder_ids & fn.EXISTS(Message2.select().where((Message.date > Message2.date) & (Message.conversationID == Message2.conversationID)))) \
			.order_by(Message.date)
		
		read_messages(query, True)


if __name__ == "__main__":
	import_thunderbird()