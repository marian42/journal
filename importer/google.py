import events
from database import db
import os
import icalendar
import json
import datetime
import dateutil
import requests


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
			events.add("Google Calendar event: " + event.get("summary"), event.get("dtstart").dt, ["google", "calendar", "event"], kvps={"location":event.get("location")}, hash=event.get("uuid"))


def read_locations(directory):
	data = json.loads(open(directory + "Location History/Location History.json").read())
	for item in data["locations"]:
		time = datetime.datetime.fromtimestamp(int(item["timestampMs"]) / 1000)
		if "latitudeE7" not in item:
			continue
		latitude = item["latitudeE7"] * 1e-7
		longitude = item["longitudeE7"] * 1e-7
		events.add("Google Location History", time, ["google", "location"], latitude=latitude, longitude=longitude)


def read_saved_places(directory):
	data = json.loads(open(directory + "Maps (your places)/Saved Places.json").read())
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
		events.add("Liked " + str(len(likes)) + " videos :" + likes[0].title + " and " + str(len(likes) - 1) + (" others." if len(likes) > 2 else " other."), likes[0].time, ["youtube", "like"],
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


def import_google(directory="data/google/"):
	with db.atomic():
		read_calendar(directory)
		read_locations(directory)
		#read_saved_places(directory)
		read_youtube_uploads(directory)
		read_youtube_subscriptions(directory)
		read_youtube_favorites(directory)
		read_youtube_likes(directory)
		read_youtube_playlists(directory)


if __name__ == "__main__":
	import_google()