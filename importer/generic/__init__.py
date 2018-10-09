import csv
import dateutil
import events
from database import db


def populate_csv_string(string, line):
	result = string
	for i in range(len(line)):
		result = result.replace("{" + str(i) + "}", line[i])
	return result


def import_csv(filename, time_index, summary, tags, kvps, skip_first_line = True, delimiter = ",", dayfirst = False):
	file = open(filename, encoding = "utf-8")
	reader = csv.reader(file, delimiter = delimiter)
	
	if skip_first_line:
		next(reader, None)
	
	with db.atomic():
		for line in reader:
			current_summary = populate_csv_string(summary, line)
			current_kvps = {key: populate_csv_string(kvps[key], line) if (type(kvps[key]) is str) else line[kvps[key]] for key in kvps}
			time = dateutil.parser.parse(line[time_index], dayfirst = dayfirst)
			
			events.add(current_summary, time, tags, current_kvps)


class GroupEventItem:
	def __init__(self, time, data):
		self.time = time
		self.data = data


class GroupEvents:
	def __init__(self, interval_minutes = 60):
		self.items = dict()
		self.interval_minutes = interval_minutes
		
	def add(self, time, data, category = None):
		if category not in self.items:
			self.items[category] = []
		self.items[category].append(GroupEventItem(time, data))
	
	def create_events(self, create_single, create_many):
		for category in self.items:
			current_items = sorted(self.items[category], key = lambda item: item.time)
			batch = None
			last_time = None
			for item in current_items:
				if batch is None:
					batch = []
				elif (item.time - last_time).total_seconds() >= self.interval_minutes * 60:
					if len(batch) == 1:
						create_single(batch[0].time, batch[0].data)
					else:
						create_many(batch[0].time, [item.data for item in batch])
					batch = []
				batch.append(item)
				last_time = item.time
			if batch is not None:
				if len(batch) == 1:
					create_single(batch[0].time, batch[0].data)
				else:
					create_many(batch[0].time, [item.data for item in batch])
				
			