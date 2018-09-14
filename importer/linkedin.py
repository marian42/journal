import events
from database import db
import dateparser
import csv


def import_linkedin(directory="data/linkedin/"):
	with db.atomic():
			file = open(directory + "Connections.csv", encoding = "utf8")
			reader = csv.reader(file, delimiter = ",")
			next(reader, None)
			
			for line in reader:
				name = line[0] + " " + line[1]
				email = line[2]
				company = line[3]
				position = line[4]
				time = dateparser.parse(line[5])
				
				events.add("Added LinkedIn contact " + name + ".", time, ["linkedin", "friend"], kvps = {"email": email, "company": company, "position": position})


if __name__ == "__main__":
	import_linkedin()