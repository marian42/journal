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
