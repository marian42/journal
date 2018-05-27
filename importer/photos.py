import events
from database import db
import os
import datetime
import exifread


def get_files(directory):
	result = []
	for root, _, files in os.walk(directory):
		for item in files:
			if item.split(".")[-1].lower() in ["jpg", "png", "jpeg"]:
				result.append(str(os.path.join(root, item)))
	return result

def convert_to_degress(value):
	deg = value[0]
	deg = float(deg.num) / float(deg.den)
	
	minute = value[1]
	minute = float(minute.num) / float(minute.den)
	
	sec = value[2]
	sec = float(sec.num) / float(sec.den)
	
	return deg + (minute / 60.0) + (sec / 3600.0)

def import_photos(directory="data/photos/"):
	with db.atomic():
		for file in get_files(directory):
			tags = exifread.process_file(open(file, 'rb'))
			
			try:
				time = datetime.datetime.strptime(tags["Image DateTime"].values, "%Y:%m:%d %H:%M:%S")
			except ValueError:
				print "Bad time format: " + tags["Image DateTime"].values
				continue
			
			camera = tags["Image Make"].values + " " + tags["Image Model"].values
			
			latitude = None
			longitude = None
			if tags.has_key("GPS GPSLatitude") and tags.has_key("GPS GPSLatitudeRef") and tags.has_key("GPS GPSLongitude") and tags.has_key("GPS GPSLongitudeRef"):
				latitude = convert_to_degress(tags["GPS GPSLatitude"].values) * (1 if tags["GPS GPSLatitudeRef"].values == "N" else -1)
				longitude = convert_to_degress(tags["GPS GPSLongitude"].values) * (1 if tags["GPS GPSLongitudeRef"].values == "E" else -1)
				
			events.add("Took a picture with " + camera, time, ["photo", camera], {"camera": camera}, latitude=latitude, longitude=longitude, images=[file])

if __name__ == "__main__":
	import_photos()