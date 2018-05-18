from git import Repo, InvalidGitRepositoryError
import events
from database import db

def import_repository(directory = "data/git/test"):
	name = directory.split("/")[-1]
	
	try:
		repo = Repo(directory)
	except InvalidGitRepositoryError:
		print "Skipping " + name + ", as it's not a git repo."
		return False
	
	print "Importing repository " + name + "..."
	count = 0
	with db.atomic():
		for commit in repo.iter_commits():
			events.add("Committed to " + name + ": " + commit.summary,
				commit.committed_datetime,
				hash=commit.hexsha, tags=["git", "commit", name],
				kvps={"author": commit.author, "message": commit.message})
			count += 1
	
	print "Imported " + str(count) + " commits from repository " + name + "."
	return True

def import_repositories(directory = "data/git/"):
	import os
	
	count = 0
	for repository in [os.path.join(directory, name) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]:
		if import_repository(repository):
			count += 1
	print "Imported " + str(count) + " repositories."
	
if __name__ == "__main__":
	import_repositories()