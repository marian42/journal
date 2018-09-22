import events
from database import db
import json
import dateutil


def import_kickstarter(directory = "data/kickstarter/"):
	events.prepare_import(8)
	print("Importing Kickstarter pledges...")
	with db.atomic():
		file = open(directory + "backed_projects.json", encoding = "utf8")
		data = json.load(file)
		for project in data:
			summary = "Backed " + project["name"] + " on Kickstarter for " + project["pledge_amount"] + " " + project["project_currency"]
			time = dateutil.parser.parse(project["pledged_at"])
			
			kvps = {
				"name": project["name"],
				"description": project["description"],
				"goal": project["project_goal"],
				"status": project["project_status"],
				"amount": project["pledge_amount"],
				"currency": project["project_currency"]
			}
			
			events.add(summary, time, ["kickstarter"], kvps)


if __name__ == "__main__":
	import_kickstarter()