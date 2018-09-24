import importer.generic
import events


def import_ebay(directory = "data/ebay/"):
	events.prepare_import(14)
	print("Importing ebay purchases...")
	importer.generic.import_csv(directory + "ebay.csv", 4, "Purchased {16} from {6} for {14} {13}", ["ebay", "purchase"], {"product": 16, "category": 15, "status": 5, "amount": "{14} {13}", "seller": 6, "type": 9}, delimiter = ";", dayfirst = True)
	

if __name__ == "__main__":
	import_ebay()

