import events
from database import db
import os
import dateutil
from lxml import html

'''
How to aquire data:
In steam, click on your wallet amount, click "View licenses and product key activations".
Save this page as an html document and provide the directory it's in.
'''


def import_steam(directory="data/steam/"):
	with db.atomic():
		for file_name in [os.path.join(directory, name) for name in os.listdir(directory)]:
			tree = html.fromstring(open(file_name).read())
			table = tree.xpath("//*[@id=\"main_content\"]/div/div/div/div/table/tbody")
			for tr in table[0][1:]:
				time = dateutil.parser.parse(tr[0].text)
				name = tr[1].text.strip()
				if len(tr[1]) == 1:
					name = tr[1][-1].tail.strip()
				events.add("Added Steam game " + name + " to library.", time, ["steam", "game"], kvps={"name": name})


if __name__ == "__main__":
	import_steam()