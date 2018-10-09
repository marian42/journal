import events
from database import db
import os
import icalendar
import json
import datetime
import dateutil
import requests
import importer.generic


def download_file(url, filename):
	if os.path.isfile(filename):
		return
	request = requests.get(url, allow_redirects = True)
	with open(filename, 'wb') as file:
		file.write(request.content)


def read_calendar(directory):
	calendar_directory = directory + "Calendar/"
	
	for calendar_path in [os.path.join(calendar_directory, name) for name in os.listdir(calendar_directory)]:
		cal = icalendar.Calendar.from_ical(open(calendar_path).read())
		for event in cal.walk("vevent"):
			events.add("Google Calendar event: " + event.get("summary"), event.get("dtstart").dt, ["google", "calendar", "event"], kvps={"location":event.get("location")})


def read_locations(directory):
	data = json.loads(open(directory + "Location History/Location History.json", encoding = "utf-8").read())
	for item in data["locations"]:
		time = datetime.datetime.fromtimestamp(int(item["timestampMs"]) / 1000)
		if "latitudeE7" not in item:
			continue
		latitude = item["latitudeE7"] * 1e-7
		longitude = item["longitudeE7"] * 1e-7
		events.add("Google Location History", time, ["google", "location"], latitude=latitude, longitude=longitude)


def read_saved_places(directory):
	data = json.loads(open(directory + "Maps (your places)/Saved Places.json", encoding = "utf-8").read())
	for place in data["features"]:
		properties = place["properties"]
		url = properties["Google Maps URL"]
		latitude = 0
		longitude = 0
		if "Latitude" in properties["Location"]:
			latitude = float(properties["Location"]["Latitude"])
			longitude = float(properties["Location"]["Longitude"])
		elif "Geo Coordinates" in properties["Location"]:
			latitude = float(properties["Location"]["Geo Coordinates"]["Latitude"])
			longitude = float(properties["Location"]["Geo Coordinates"]["Longitude"])
		name = properties["Title"]
		time = dateutil.parser.parse(properties["Published"])
		events.add("Saved place with Google Maps: " + name, time, ["google", "maps", "place"], {"name": name, "url": url}, latitude=latitude, longitude=longitude)


def read_youtube_uploads(directory):
	video_directory = directory + "YouTube/videos/"
	for filename in [os.path.join(video_directory, name) for name in os.listdir(video_directory) if name.endswith(".json")]:
		json_text = open(filename, encoding = "utf8").read()
		data = json.loads(json_text)
		video = data[0]
		snippet = video["snippet"]
		time = dateutil.parser.parse(snippet["publishedAt"])
		thumbnail_key = sorted(snippet["thumbnails"].keys(), key = lambda name: snippet["thumbnails"][name]["height"], reverse = True)[0]
		thumbnail_url = snippet["thumbnails"][thumbnail_key]["url"]
		thumbnail_filename = video_directory + video["id"] + "." + thumbnail_url.split(".")[-1].split("?")[0]
		download_file(thumbnail_url, thumbnail_filename)
		
		kvps = {
			"description": snippet["description"],
			"channel": snippet["channelTitle"],
			"views": video["statistics"]["viewCount"],
			"likes": video["statistics"]["likeCount"],
			"title": snippet["title"],
			"url": "https://www.youtube.com/watch?v=" + video["id"],
			"visibility": video["status"]["privacyStatus"]
		}
		
		events.add("Uploaded video: " + snippet["title"], time, ["youtube", "video"], kvps, images = [(time, thumbnail_filename)])
		
		
def read_youtube_subscriptions(directory):
	json_text = open(directory + "Youtube/subscriptions/subscriptions.json", encoding = "utf8").read()
	data = json.loads(json_text)
	for subscription in data:
		snippet = subscription["snippet"]
		time = dateutil.parser.parse(snippet["publishedAt"])
		
		kvps = {
			"description": snippet["description"],
			"channel": snippet["title"],
			"url": "https://www.youtube.com/channel/" + snippet["resourceId"]["channelId"]
		}
		
		events.add("Subscribed to " + snippet["title"] + " on Youtube.", time, ["youtube", "subscription"], kvps)


def read_youtube_playlist(filename, name):
	json_text = open(filename, encoding = "utf8").read()
	data = json.loads(json_text)
	for item in data:
		snippet = item["snippet"]
		time = dateutil.parser.parse(snippet["publishedAt"])
		kvps = {
			"description": snippet["description"],
			"title": snippet["title"],
			"url": "https://www.youtube.com/watch?v=" + item["contentDetails"]["videoId"] + "&index=" + str(snippet["position"]) + "&list=" + snippet["playlistId"]
		}
		events.add("Added video to " + name + ": " + snippet["title"], time, ["youtube", name.lower()], kvps)


def read_youtube_favorites(directory):
	read_youtube_playlist(directory + "YouTube/playlists/Favorites.json", "Favorites")


class YoutubeLike:
	def __init__(self, time, title, url):
		self.time = time
		self.title = title
		self.url = url


def create_like_event(likes):
	if len(likes) == 1:
		events.add("Liked video: " + likes[0].title, likes[0].time, ["youtube", "like"], kvps = {"title": likes[0].title, "url": likes[0].url})
	else:
		events.add("Liked " + str(len(likes)) + " videos: " + likes[0].title + " and " + str(len(likes) - 1) + (" others." if len(likes) > 2 else " other."), likes[0].time, ["youtube", "like"],
			kvps = {"titles": "\n".join([like.title for like in likes]), "url": likes[0].url, "urls": "\n".join([like.url for like in likes])})


def read_youtube_likes(directory, group_minutes = 180):
	json_text = open(directory + "YouTube/playlists/likes.json", encoding = "utf8").read()
	data = json.loads(json_text)
	
	likes = []
	for item in data:
		snippet = item["snippet"]
		time = dateutil.parser.parse(snippet["publishedAt"])
		url = "https://www.youtube.com/watch?v=" + item["contentDetails"]["videoId"] + "&index=" + str(snippet["position"]) + "&list=" + snippet["playlistId"]
		likes.append(YoutubeLike(time, snippet["title"], url))
	
	group_seconds = group_minutes * 60
	likes.sort(key = lambda l: l.time)
	
	last_time = None
	group = []
	
	for like in likes:
		if last_time is not None and (like.time - last_time).total_seconds() > group_seconds:
			create_like_event(group)
			group = []
		group.append(like)
		last_time = like.time
		
	if any(group):
		create_like_event(group)
	

def read_youtube_playlists(directory):
	playlist_directory = directory + "YouTube/playlists/"
	for filename in [os.path.join(playlist_directory, name) for name in os.listdir(playlist_directory) if name.endswith(".json")]:
		if filename.endswith("Favorites.json") or filename.endswith("likes.json") or filename.endswith("watch-later.json") or filename.endswith("uploads.json"):
			continue
		name = ".".join(filename.split("/")[-1].split(".")[0:-1])
		read_youtube_playlist(filename, name)


def read_device_activations(directory):
	activation_directory = directory + "Android Device configuration service"
	for filename in [os.path.join(activation_directory, name) for name in os.listdir(activation_directory) if name.endswith(".html")]:
		with open(filename, "r") as file:
			lines = [line.strip() for line in file.readlines()]
		data = {}
		for line in lines:
			if not line.endswith("<br/>"):
				continue
			line = line[0:-5]
			items = line.split(":")
			if len(items) < 2:
				continue
			data[items[0]] = ":".join(items[1:]).strip()
		time = dateutil.parser.parse(data["Registration Time"])
		kvps = {
			"model": data["Model"],
			"manufacturer": data["Manufacturer"],
			"device": data["Device"],
			"product": data["Product"],
			"type": data["Device Type"]
		}
		events.add("Registered " + data["Device Type"] + ": " + data["Manufacturer"] + " " + data["Model"], time, ["google", "device", "android"], kvps)


def read_transactions(directory):
	transaction_directory = directory + "Google Pay\Transactions made on Google"
	for filename in [os.path.join(transaction_directory, name) for name in os.listdir(transaction_directory) if name.endswith(".csv")]:
		importer.generic.import_csv(filename, 0, "Purchased {2} from {3} for {6}", ["google", "purchase", "google-pay"], {"product": 2, "domain": 3, "status": 5, "amount": 6})


def read_google_play_devices(directory):
	json_text = open(directory + "Google Play Store/Devices.json", encoding = "utf8").read()
	device_data = json.loads(json_text)
	for device in device_data:
		time = dateutil.parser.parse(device["device"]["deviceRegistrationTime"])
		data = device["device"]["mostRecentData"]
		kvps = {
			"carrier": data["carrierName"],
			"manufacturer": data["manufacturer"],
			"model": data["modelName"],
			"device": data["deviceName"],
			"product": data["productName"]
		}
		events.add("Registered Google Play device " + data["manufacturer"] + " " + data["modelName"] + ".", time, ["google", "googleplay", "device"], kvps)
		

def read_google_play_installs(directory):
	json_text = open(directory + "Google Play Store/Installs.json", encoding = "utf8").read()
	install_data = json.loads(json_text)
	
	group_importer = importer.generic.GroupEvents()
	
	for install in [item["install"] for item in install_data]:
		time = dateutil.parser.parse(install["firstInstallationTime"])
		name = install["doc"]["title"]
		device = install["deviceAttribute"]["deviceDisplayName"]
		group_importer.add(time, (name, device), device)
	
	group_importer.create_events(
		create_single = lambda time, data: events.add("Installed " + data[0] + " on " + data[1], time, ["google", "googleplay", "install"], {"app": data[0], "device": data[1]}),
		create_many = lambda time, data: events.add("Installed " + data[0][0] + " and " + str(len(data) - 1) + " other " + ("app" if len(data) == 2 else "apps") +  " on " + data[0][1], time, ["google", "googleplay", "install"], {"apps": "\n".join([item[0] for item in data]), "device": data[0][1]})
	)


def read_google_play(directory):
	read_google_play_devices(directory)
	read_google_play_installs(directory)
	

def import_google(directory="data/google/"):
	events.prepare_import(9)
	with db.atomic():
		print("Importing google calendar...")
		read_calendar(directory)
		#read_locations(directory)
		print("Importing saved places...")
		read_saved_places(directory)
		print("Importing Youtube uploads...")
		read_youtube_uploads(directory)
		print("Importing Youtube subscriptions...")
		read_youtube_subscriptions(directory)
		print("Importing Youtube favorites...")
		read_youtube_favorites(directory)
		print("Importing Youtube Likes...")
		read_youtube_likes(directory)
		print("Importing Youtube Playlists...")
		read_youtube_playlists(directory)
		print("Importing Google device activations...")
		read_device_activations(directory)
		print("Importing Google Pay transactions...")
		read_transactions(directory)
		print("Importing Google Play store activity...")
		read_google_play(directory)


if __name__ == "__main__":
	import_google()
