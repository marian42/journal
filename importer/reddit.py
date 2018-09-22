import praw
import json
import os
from database import db
import events
import datetime
import configparser


def get_data(directory):
	config = configparser.ConfigParser()
	config.read(directory + "reddit.ini")
	
	reddit = praw.Reddit(client_id=config["reddit"]["client_id"], client_secret=config["reddit"]["client_secret"], user_agent=config["reddit"]["user_agent"])
	user = reddit.redditor(config["reddit"]["user_name"])
	
	print("Fetching reddit submissions...")
	submissions = []
	for submission in user.submissions.new():
		data = {
			"time": submission.created_utc,
			"comments": submission.num_comments,
			"url": "https://reddit.com" + submission.permalink,
			"score": submission.score,
			"text": submission.selftext,
			"subreddit": "/" + submission.subreddit_name_prefixed,
			"title": submission.title,
			"content_url": submission.url,
			"id": submission.id
		}
		submissions.append(data)
	
	with open(directory + 'submissions.json', 'w') as outfile:
		json.dump(submissions, outfile)
	
	print("Fetching reddit comments...")
	comments = []
	for comment in user.comments.new(limit = None):
		data = {
			"time": comment.created_utc,
			"message": comment.body,
			"controversial": comment.controversiality,
			"submission_author": comment.link_author,
			"is_op": comment.is_submitter,
			"submission_url": comment.link_permalink,
			"submission_content_url": comment.link_url,
			"submission_title": comment.link_title,
			"url": "https:reddit.com" + comment.permalink,
			"score": comment.score,
			"subreddit": "/" + comment.subreddit_name_prefixed,
			"parent": comment.parent_id,
			"id": comment.id
		}
		comments.append(data)
	
	with open(directory + 'comments.json', 'w') as outfile:
		json.dump(comments, outfile)
		

def create_comment_summary(comment, char_limit = 100):
	lines = comment.split("\n")
	lines = [line.strip() for line in lines if not line.startswith(">")]
	result = " ".join(lines)
	if len(result) > char_limit:
		return result[0:char_limit] + "..."
	else:
		return result
	
	
def import_reddit(directory = "data/reddit/"):
	if not os.path.isfile(directory + "submissions.json") or not os.path.isfile(directory + "comments.json"):
		get_data(directory)
	
	with db.atomic():
		json_text = open(directory + "submissions.json").read()
		submissions = json.loads(json_text)
		
		print("Importing reddit submissions...")
		for submission in submissions:
			time = datetime.datetime.fromtimestamp(submission["time"])
			events.add("Posted to " + submission["subreddit"] + ": " + submission["title"], time, ["reddit", "post", submission["subreddit"]], kvps = {k:submission[k] for k in submission if k != "time"}, hash = submission["id"])
		
		json_text = open(directory + "comments.json").read()
		comments = json.loads(json_text)
		
		print("Importing reddit comments...")
		for comment in comments:
			time = datetime.datetime.fromtimestamp(comment["time"])
			events.add("Commented in " + comment["subreddit"] + ": " + create_comment_summary(comment["message"]), time,
			           ["reddit", "comment", comment["subreddit"]],
			           kvps = {k: comment[k] for k in comment if k != "time"}, hash = comment["id"])


if __name__ == "__main__":
	import_reddit()
