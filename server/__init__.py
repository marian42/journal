from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file, send_from_directory
from peewee import *
import os

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
	image_query = Image.select().where(Image.event == event)
	images = [image.id for image in image_query]
	
	return {
		"id": event.id,
		"summary": event.summary,
		"time": event.get_time().timestamp() * 1000,
		"tags": event.get_tags(),
		"url": event.get_value("url"),
		"images": images
	}


@app.route("/api/events")
def get_events():
	time = request.args.get('time')
	before = request.args.get('before') == 'true'
	date = datetime.datetime.fromtimestamp(float(time) / 1000.0)
	n = 100
	if before:
		query = Event.select().where(Event.time < date).order_by(Event.time.desc())[:n]
	else:
		query = Event.select().where(Event.time > date).order_by(Event.time)[:n]
	result = [to_dict(event) for event in query]
	if before:
		result = reversed(result)
	
	return jsonify(list(result))


@app.route("/api/details")
def get_data():
	event_id = request.args.get('id')
	
	query = KeyValuePair.select().where(KeyValuePair.event == event_id)
	
	result = {}
	for item in query:
		result[item.key.name] = item.value
	
	return jsonify(result)


@app.route("/api/preview/<id>")
def get_preview(id):
	image = Image.get(Image.id == id)
	image.create_thumbnail()
	filename = image.get_thumbnail_filename()
	return send_file(os.path.join(os.getcwd(), filename))


@app.route("/api/image/<id>")
def get_image(id):
	image = Image.get(Image.id == id)
	filename = image.file
	print(filename)
	return send_file(os.path.join(os.getcwd(), filename))
	

if __name__ == '__main__':
	app.run()
