import events
from database import db
import os
import icalendar
import json
import datetime
import dateutil


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
	

def import_google(directory="data/google/"):
	with db.atomic():
		read_calendar(directory)
		#read_locations(directory)
		read_saved_places(directory)


if __name__ == "__main__":
	import_google()