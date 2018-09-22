import events
from database import db
import os
import datetime
import exifread


class Photo:
	def __init__(self, file, time, camera, latitude, longitude):
		self.file = file
		self.time = time
		self.camera = camera
		self.latitude = latitude
		self.longitude = longitude
		

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


def find_photos(directory):
	result = []
	
	count = 0
	last_update = datetime.datetime.now()
	print("Importing images from " + directory + "...")
	for file in get_files(directory):
		tags = exifread.process_file(open(file, 'rb'))
		
		try:
			time = datetime.datetime.strptime(tags["Image DateTime"].values, "%Y:%m:%d %H:%M:%S")
		except ValueError:
			print("Bad time format: " + tags["Image DateTime"].values)
			continue
		except KeyError:
			print("Image has no EXIF data. Skipping. " + file)
			continue
		
		camera = "Camera"
		if "Image Model" in tags:
			camera = tags["Image Model"].values
			if "Image Make" in tags:
				camera = tags["Image Make"].values + " " + camera
		
		latitude = None
		longitude = None
		if "GPS GPSLatitude" in tags and "GPS GPSLatitudeRef" in tags and "GPS GPSLongitude" in tags and "GPS GPSLongitudeRef" in tags:
			latitude = convert_to_degress(tags["GPS GPSLatitude"].values) * (
				1 if tags["GPS GPSLatitudeRef"].values == "N" else -1)
			longitude = convert_to_degress(tags["GPS GPSLongitude"].values) * (
				1 if tags["GPS GPSLongitudeRef"].values == "E" else -1)
		
		result.append(Photo(file, time, camera, latitude, longitude))
		
		count += 1
		if (datetime.datetime.now() - last_update).total_seconds() > 5:
			last_update = datetime.datetime.now()
			print(str(count) + " images found...")
			
	return result


def create_event(photos, camera):
	image_list = [(photo.time, photo.file) for photo in photos]
	time = photos[0].time
	latitude = photos[0].latitude
	longitude = photos[0].longitude
	
	if len(photos) == 1:
		events.add("Took a picture with " + camera + ".", time, ["photo", camera], {"camera": camera}, latitude=latitude, longitude=longitude, images=image_list)
	else:
		events.add("Took " + str(len(photos)) + " pictures with " + camera + ".", time, ["photo", camera], {"camera": camera}, latitude=latitude, longitude=longitude, images=image_list)


def import_photos(directory="data/photos/", session_time_seconds=60 * 60):
	events.prepare_import(4)
	photos = find_photos(directory)
	print("Sorting photos...")
	photos = sorted(photos, key=lambda p: p.time)

	with db.atomic():
		print("Importing photos...")
		last_photo_time = {}
		current_photos = {}
		
		for photo in photos:
			camera = photo.camera
			if camera not in last_photo_time:
				last_photo_time[camera] = photo.time
				current_photos[camera] = [photo]
			elif (photo.time - last_photo_time[camera]).total_seconds() > session_time_seconds:
				create_event(current_photos[camera], camera)
				last_photo_time[camera] = photo.time
				current_photos[camera] = [photo]
			else:
				last_photo_time[camera] = photo.time
				current_photos[camera].append(photo)
		
		for camera in current_photos:
			create_event(current_photos[camera], camera)


if __name__ == "__main__":
	import_photos()
