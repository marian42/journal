from git import Repo, InvalidGitRepositoryError
import events
from database import db
import os


def get_remote_url(repo):
	for remote in repo.remotes:
		for url in remote.urls:
			return url
	return None


def import_repository(directory, emails=None):
	name = directory.split("/")[-1]
	
	try:
		repo = Repo(directory)
	except InvalidGitRepositoryError:
		print("Skipping " + name + ", as it's not a git repo.")
		return False
	
	remote_url = get_remote_url(repo)
	
	print("Importing repository " + name + "...")
	count = 0
	with db.atomic():
		for commit in repo.iter_commits():
			if emails is not None and commit.author.email not in emails:
				continue
			
			kvps = {"author": commit.author, "message": commit.message, "sha": commit.hexsha}
			if remote_url is not None:
				kvps["url"] = remote_url + "/commit/" + commit.hexsha
			events.add("Committed to " + name + ": " + commit.summary,
				commit.committed_datetime,
				tags=["git", "commit", name],
				kvps=kvps)
			count += 1
	
	print("Imported " + str(count) + " commits from repository " + name + ".")
	return True


def import_repositories(directory="data/git/"):
	events.prepare_import(10)
	
	emails = None
	if os.path.isfile(directory + "emails.txt"):
		with open(directory + "emails.txt", "r") as file:
			emails = [email.strip() for email in file.readlines()]
	
	count = 0
	for repository in [os.path.join(directory, name) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
		if import_repository(repository, emails):
			count += 1
	print("Imported " + str(count) + " repositories.")

	
if __name__ == "__main__":
	import_repositories()
