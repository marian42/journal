from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file, send_from_directory
from peewee import *
import os
import json

import database

from model.event import Event
from model.keyvaluepair import KeyValuePair
from model.image import Image
from model.tagtoevent import TagToEvent
from model.tag import Tag

import datetime

from server.calendar_graph import CalendarGraph


database.init()
app = Flask(__name__, static_folder='../client/', static_url_path='')


@app.route('/')
def root():
	return app.send_static_file('index.html')


graph = None


@app.route("/api/days")
def get_days():
	global graph
	
	filter_include = request.args.get('include') == "true"
	tag_ids = [Tag.get_tag(tag).id for tag in json.loads(request.args.get('tags'))]
	
	if graph is None or graph.outdated(filter_include, tag_ids):
		graph = CalendarGraph(filter_include, tag_ids)
	return jsonify(graph.to_dict())


def to_dict(event):
	image_query = Image.select().where(Image.event == event).order_by(Image.time)
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
	try:
		date = datetime.datetime.fromtimestamp(float(time) / 1000.0)
	except OSError:
		date = datetime.datetime.min
	
	filter_include = request.args.get('include') == "true"
	tag_ids = [Tag.get_tag(tag).id for tag in json.loads(request.args.get('tags'))]
	filter_query = fn.EXISTS(TagToEvent.select().where(TagToEvent.tag.in_(tag_ids) & (TagToEvent.event == Event.id)))
	if not filter_include:
		filter_query = ~ filter_query
	
	n = 100
	if any(tag_ids):
		if before:
			query = Event.select().where((Event.time < date) & filter_query).order_by(Event.time.desc())[:n]
		else:
			query = Event.select().where((Event.time > date) & filter_query).order_by(Event.time)[:n]
	else:
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
	return send_file(os.path.join(os.getcwd(), filename))
	

if __name__ == '__main__':
	app.run()
