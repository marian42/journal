from database import db

import json


class CalendarGraph:
	def __init__(self):
		self.data = {}
		self.max = None
		self.first = None
		self.last = None
		
		cursor = db.execute_sql(
			'SELECT strftime("%Y.%m.%d", "t1"."time") AS "day", COUNT("t1"."id") AS "count" FROM "event" AS "t1" GROUP BY "day"')
		for row in cursor.fetchall():
			date = tuple(int(v) for v in row[0].split("."))
			year, month, day = date
			
			if year not in self.data:
				self.data[year] = {}
			if month not in self.data[year]:
				self.data[year][month] = {}
				
			value = row[1]
			if self.max is None:
				self.max = value
				self.first = date
			elif value > self.max:
				self.max = value
			
			self.data[year][month][day] = value
			self.last = date

	def to_dict(self):
		return {"first": self.first, "last": self.last, "max": self.max, "data": self.data}
