from database import db

import json


class CalendarGraph:
	def __init__(self, filter_include = True, filter_tags = []):
		self.data = {}
		self.max = None
		self.first = None
		self.last = None
		
		self.filter_include = filter_include
		self.filter_tags = filter_tags
		
		subquery = '"event"'
		if len(filter_tags) != 0:
			subquery = '(SELECT * FROM "event" AS t1 WHERE ' + ('' if filter_include else 'NOT ') + 'EXISTS (SELECT "t2"."tag_id", "t2"."event_id" FROM "tagtoevent" as "t2" WHERE ("t1"."id" == "t2"."event_id" AND "t2"."tag_id" IN (' + ', '.join([str(tag) for tag in filter_tags]) + '))))'

		cursor = db.execute_sql('SELECT strftime("%Y.%m.%d", "t1"."time") AS "day", COUNT("t1"."id") AS "count" FROM ' + subquery + ' AS "t1" GROUP BY "day"')
		
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
			
	def outdated(self, filter_include, filter_tags):
		return filter_include != self.filter_include or set(filter_tags) != set(self.filter_tags)

	def to_dict(self):
		return {"first": self.first, "last": self.last, "max": self.max, "data": self.data}
