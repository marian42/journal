import events
from database import db
import json
import datetime
import os

def load_to_json(filename):
	json_data = open(filename).read()
	return json.loads(json_data)

def read_app_posts(directory):
	data = load_to_json(directory + "apps/posts_from_apps.json")
	for post in data["app_posts"]:
		attachment_data = post["attachments"][0]["data"][0]["external_context"]
		time = datetime.datetime.fromtimestamp(post["timestamp"])
		message = attachment_data["name"]
		title = post["title"]
		app_name = "unknown app"
		if "via" in title:
			app_name = title[title.index("via") + 4 : -1]
		
		kvps = {"message": message, "title": title, "app": app_name}
		if attachment_data.has_key("url"):
			kvps["url"] = attachment_data["url"]
		events.add("Facebook post via " + app_name + ": " + message, time, ["facebook", "post", "app"], kvps)

def read_app_installs(directory):
	data = load_to_json(directory + "apps/installed_apps.json")
	for item in data["installed_apps"]:
		events.add("Added Facebook app " + item["name"] + ".", datetime.datetime.fromtimestamp(item["time_added"]), ["facebook", "app"], {"app": item["name"]})
		
def read_comments(directory):
	data = load_to_json(directory + "comments/comments.json")
	for comment in data["comments"]:
		time = datetime.datetime.fromtimestamp(comment["timestamp"])
		message = comment["data"][0]["comment"]["comment"]
		events.add("Facebook: " + comment["title"], time, ["facebook", "comment"], {"message": message})
		
def read_events(directory):
	data = load_to_json(directory + "events/event_responses.json")
	for event in data["event_responses"]["events_joined"]:
		time = datetime.datetime.fromtimestamp(event["start_timestamp"])
		name = event["name"]
		events.add("Participated in Facebook event: " + name, time, ["facebook", "event"], {"name": name})
	
	data = load_to_json(directory + "events/your_events.json")
	for event in data["your_events"]:
		time = datetime.datetime.fromtimestamp(event["start_timestamp"])
		name = event["name"]
		location = event["place"]["name"]
		events.add("Hosted Facebook event: " + name, time, ["facebook", "event"], {"name": name, "location": location, "message": event["description"]})
		
def read_friends(directory):
	data = load_to_json(directory + "friends/friends_added.json")
	for friend in data["friends"]:
		time = datetime.datetime.fromtimestamp(friend["timestamp"])
		name = friend["name"]
		events.add("Added Facebook friend " + name + ".", time, ["facebook", "friend"], {"name": name})

def create_conversation_event(title, message_count, time, participants, history, first):
	kvps = {"participants": participants, "message": history}
	if first:
		events.add(
			"Started a Facebook conversation with " + title + " (" + str(message_count) + " message" + (
				"s" if message_count > 1 else "") + ").",
			time, ["facebook", "message"], kvps)
	else:
		events.add(
			"Exchanged " + str(message_count) + " Facebook message" + (
				"s" if message_count > 1 else "") + " with " + title + ".",
			time, ["facebook", "message"], kvps)

def read_messages(directory):
	message_directory = directory + "messages/"
	for conversation in [os.path.join(message_directory, name) for name in os.listdir(message_directory) if os.path.isdir(os.path.join(message_directory, name)) and name != "stickers_used"]:
		data = load_to_json(conversation + "/message.json")
		if not data.has_key("title"):
			continue
		title = data["title"]
		participants = [title]
		if data.has_key("participants"):
			participants =  data["participants"]
		messages = data["messages"]
		session_start_time = None
		last_message_time = None
		history = ""
		message_count = 0
		session_count = 0
		
		for message in reversed(messages):
			if message.has_key("content"):
				message_time = datetime.datetime.fromtimestamp(message["timestamp"])
				if session_start_time is None:
					session_start_time = message_time
				elif (message_time - last_message_time).total_seconds() > 4 * 60 * 60:
					create_conversation_event(title, message_count, session_start_time, ", ".join(participants), history, session_count == 0)
					
					session_start_time = message_time
					message_count = 0
					session_count += 1
					history = ""
				last_message_time = message_time
				message_count += 1
				history += message["sender_name"] + ": " + message["content"] + "\n"
			if message.has_key("photos") and not message["sender_name"] in participants:
				events.add("Sent " + (str(len(message["photos"])) + " images" if len(message["photos"]) > 1 else "an image") + " to " + title + ".",
				           datetime.datetime.fromtimestamp(message["timestamp"]),
				           ["facebook", "message", "image"], kvps={"participants": ", ".join(participants)}, images=[directory + photo["uri"] for photo in message["photos"]])
			if message.has_key("photos") and message["sender_name"] in participants:
				events.add("Received " + (str(len(message["photos"])) + " images" if len(
					message["photos"]) > 1 else "an image") + " from " +  message["sender_name"] + ".",
				           datetime.datetime.fromtimestamp(message["timestamp"]),
				           ["facebook", "message", "image"], kvps={"participants": ", ".join(participants)},
				           images=[photo["uri"] for photo in message["photos"]])
				
		create_conversation_event(title, message_count, session_start_time, ", ".join(participants), history, session_count == 0)
		
def read_photos(directory):
	photo_directory = directory + "photos/album/"
	for album_file in [os.path.join(photo_directory, name) for name in os.listdir(photo_directory)]:
		data = load_to_json(album_file)
		album_name = data["name"]
		for photo in data["photos"]:
			file = directory + photo["uri"]
			metadata = photo["media_metadata"]["photo_metadata"]
			time = datetime.datetime.fromtimestamp(metadata["taken_timestamp"]) if metadata.has_key("taken_timestamp") else datetime.datetime.fromtimestamp(metadata["modified_timestamp"])
			
			tags = ["facebook", "photo"]
			kvps = {}
			if metadata.has_key("camera_make") and metadata.has_key("camera_model"):
				camera = metadata["camera_make"] + " " + metadata["camera_model"]
				tags.append(camera)
				kvps["camera"] = camera
			
			events.add("Added photo to Facebook album " + album_name + ".",
			           time,
			           tags,
			           kvps,
			           hash=file,
			           latitude=(metadata["latitude"] if metadata.has_key("latitude") else None),
			           longitude=(metadata["longitude"] if metadata.has_key("longitude") else None),
			           images=[file])


def import_facebook_data(directory = "data/facebook/"):
	with db.atomic():
		print "Reading Facebook app posts..."
		read_app_posts(directory)
		read_app_installs(directory)
		print "Reading Facebook comments..."
		read_comments(directory)
		print "Reading Facebook events..."
		read_events(directory)
		print "Reading Facebook friends..."
		read_friends(directory)
		print "Reading Facebook messages..."
		read_messages(directory)
		print "Reading Facebook photos..."
		read_photos(directory)


if __name__ == "__main__":
	import_facebook_data()