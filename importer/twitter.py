import events
from database import db
import os
import json
import dateutil
import urllib


def import_twitter(directory="data/twitter/"):
	with db.atomic():
		tweets_directory = directory + "data/js/tweets/"
		
		for tweet_file in [os.path.join(tweets_directory, name) for name in os.listdir(tweets_directory)]:
			lines = open(tweet_file).read().split("\n")
			data = json.loads("\n".join(lines[1:]))
			for tweet in data:
				hash = tweet["id_str"]
				text = tweet["text"]
				is_reply = "in_reply_to_screen_name" in tweet
				is_retweet = "retweeted_status" in tweet
				time = dateutil.parser.parse(tweet["created_at"])
				images = []
				hashtags = [item["text"] for item in tweet["entities"]["hashtags"]]
				kvps = {"text": text, "url": "https://twitter.com/" + tweet["user"]["screen_name"] + "/status/" + hash}
				
				for image in tweet["entities"]["media"]:
					url = image["media_url_https"]
					extension = url.split(".")[-1]
					url += ":orig"
					local_address = directory + "img/" + image["id_str"] + "." + extension
					if not os.path.isfile(local_address):
						urllib.urlretrieve(url, local_address)
					images.append((time, local_address))
				
				if is_retweet:
					events.add("Retweeted " + tweet["retweeted_status"]["user"]["name"] + ": " + text, time, ["twitter", "retweet"] + hashtags, kvps, hash, images = images)
				elif is_reply:
					events.add("Replied to " + tweet["in_reply_to_screen_name"] + ": " + text, time, ["twitter", "reply"] + hashtags, kvps, hash, images=images)
				else:
					events.add("Tweet: " + text, time, ["twitter", "tweet"] + hashtags, kvps, hash, images=images)
				
				

if __name__ == "__main__":
	import_twitter()