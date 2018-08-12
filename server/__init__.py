from flask import Flask
from flask import jsonify
from flask import request
from peewee import *

from database import db

from model.event import Event
from model.image import Image
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.tag import Tag
from model.tagtoevent import TagToEvent
from model.image import Image

import datetime

from server.calendar_graph import CalendarGraph

app = Flask(__name__, static_folder='../client/', static_url_path='')


@app.route('/')
def root():
	return app.send_static_file('index.html')

graph = None

@app.route("/api/days")
def get_days():
	global graph
	if graph is None:
		graph = CalendarGraph()
	return jsonify(graph.to_dict())


def to_dict(event):
	return {
		"summary": event.summary,
		"time": event.get_time().timestamp() * 1000
	}


@app.route("/api/events")
def get_events():
	time = request.args.get('time')
	before = request.args.get('before') == 'true'
	date = datetime.datetime.fromtimestamp(float(time) / 1000.0)
	print(date)
	n = 100
	if before:
		query = Event.select().where(Event.time < date).order_by(Event.time.desc())[:n]
	else:
		query = Event.select().where(Event.time > date).order_by(Event.time)[:n]
	result = [to_dict(event) for event in query]
	if before:
		result = reversed(result)
	
	return jsonify(list(result))
		
	
	
	

if __name__ == '__main__':
	app.run()
