from flask import Flask
from flask import jsonify
from peewee import *

from database import db

from model.event import Event
from model.image import Image
from model.key import Key
from model.keyvaluepair import KeyValuePair
from model.tag import Tag
from model.tagtoevent import TagToEvent
from model.image import Image

from server.calendar_graph import CalendarGraph

import json
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


if __name__ == '__main__':
	app.run()
