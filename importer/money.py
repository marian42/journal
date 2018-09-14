import events
from database import db
import os
import datetime

currencies = {"EUR": "\u20AC", "USD": "$"}


def import_money(directory="data/money/"):
	with db.atomic():
		for file_name in [os.path.join(directory, name) for name in os.listdir(directory)]:
			lines = open(file_name).read().split("\n")
			for line in lines[1:-1]:
				data = [value[1:-1] for value in line.split(";")]
				account = data[0]
				time = datetime.datetime.strptime(data[1], "%d.%m.%y")
				message = data[4].split("+")[-1]
				recipient_name = data[5]
				recipient_account = data[6]
				recipient_bank = data[7]
				amount = data[8].replace(",", ".")
				amount_positive = amount[0] != "-"
				amount_absolute = amount.replace("-", "")
				currency = data[9]
				if currency in currencies:
					currency = currencies[currency]
				kvps = {"account": account, "message": message, "recipient-name": recipient_name, "recipient-account": recipient_account, "recipient-bank": recipient_bank, "amount": amount}
				if len(recipient_name) == 0:
					continue
				if amount_positive:
					events.add("Received " + currency + " " + amount_absolute + " from " + recipient_name + ": " + message, time, ["money"], kvps)
				else:
					events.add("Sent " + currency + " " + amount_absolute + " to " + recipient_name + ": " + message, time, ["money"], kvps)

if __name__ == "__main__":
	import_money()