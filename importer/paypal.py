import events
from database import db
import os
import datetime

currencies = {"EUR": "\u20AC", "USD": "$"}


def import_paypal(directory="data/paypal/"):
	events.prepare_import(5)
	print("Importing Paypal payments...")
	with db.atomic():
		for file_name in [os.path.join(directory, name) for name in os.listdir(directory)]:
			lines = open(file_name, encoding = "utf8").read().split("\n")
			for line in lines[1:-1]:
				data = [value for value in line[1:-1].split('","')]
				time = datetime.datetime.strptime(data[0] + " " + data[1], "%d.%m.%Y %H:%M:%S")
				name = data[3]
				if len(name) == 0 or data[4] == "Allgemeine Autorisierung":
					continue
				currency = data[6]
				if currency in currencies:
					currency = currencies[currency]
				amount = data[9].replace(",", ".")
				if len(amount) == 0:
					continue
				amount_positive = amount[0] != "-"
				amount_absolute = amount.replace("-", "")
				item = data[15]
				
				kvps = {"account": data[10], "message": item, "recipient-name": name,
				        "recipient-account": data[11], "amount": amount}
								
				if amount_positive:
					events.add("Received " + currency + " " + amount_absolute + " from " + name + (" for " + item if len(item) > 0 else "") + " using Paypal.", time, ["money", "paypal"], kvps)
				else:
					events.add("Paid " + currency + " " + amount_absolute + " to " + name + (" for " + item if len(item) > 0 else "") + " using Paypal.", time, ["money", "paypal"], kvps)


if __name__ == "__main__":
	import_paypal()
