import events
from database import db
import os
from xml.etree import ElementTree
import dateutil
import re

def import_wordpress(directory="data/wordpress/"):
	with db.atomic():
		for file_name in [os.path.join(directory, name) for name in os.listdir(directory)]:
			tree = ElementTree.parse(file_name)
			channel = tree.find("channel")
			
			for item in channel:
				if item.tag != "item":
					continue
				title = item.find("title").text
				time = dateutil.parser.parse(item.find("pubDate").text)
				url = item.find("guid").text
				content = next(element.text for element in item if element.tag.endswith("encoded"))
				content = re.sub("[\<].*?[\>]", "", content)
				
				tags = [element.text for element in item if element.tag == "category"]
				events.add("Posted Wordpress article: " + title, time, ["wordpress"] + list(set(tags)), {"title": title, "message": content, "url": url})


if __name__ == "__main__":
	import_wordpress()