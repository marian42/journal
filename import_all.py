import importer.thunderbird
import importer.whatsapp
import importer.facebook
import importer.google
import importer.money
import importer.paypal
import importer.photos
import importer.steam
import importer.twitter
import importer.wordpress
import importer.gitrepo
import importer.linkedin
import importer.kickstarter
import importer.reddit


def import_all():
	importer.thunderbird.import_thunderbird()
	importer.whatsapp.import_whatsapp()
	importer.facebook.import_facebook_data()
	importer.google.import_google()
	importer.money.import_money()
	importer.paypal.import_paypal()
	importer.photos.import_photos()
	importer.steam.import_steam()
	importer.twitter.import_twitter()
	importer.wordpress.import_wordpress()
	importer.gitrepo.import_repositories()
	importer.linkedin.import_linkedin()
	importer.wordpress.import_wordpress()
	importer.kickstarter.import_kickstarter()
	importer.reddit.import_reddit()


if __name__ == "__main__":
	import_all()