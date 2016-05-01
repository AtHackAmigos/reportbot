#!venv/bin/python
import os
from flask import Flask, render_template, request
from model import connect, db, Registry, Event, Log
from sms import handle_sms_callback
import json
from flask import jsonify
from datetime import datetime, date, time, timedelta
app = Flask(__name__)


@app.route('/api/sms', methods=['GET', 'POST'])
def record_sms():
  return handle_sms_callback(request)


@app.route('/map')
def map():
  return render_template('map.html')


@app.route('/')
def home():
  registry = Registry.query.all()
  data = data_to_display(registry)
  return render_template('homepage.html', registry=registry,data=data)

@app.route('/hired.json')
def phone_data():
  hired1 = Event.query.filter_by(event_type=1).filter(Event.timestamp.between(datetime.now()-timedelta(minutes=1), datetime.now())).all()
  hired2 = Event.query.filter_by(event_type=1).filter(Event.timestamp.between(datetime.now()-timedelta(minutes=2), datetime.now()-timedelta(minutes=1))).all()
  hired3 = Event.query.filter_by(event_type=1).filter(Event.timestamp.between(datetime.now()-timedelta(minutes=3), datetime.now()-timedelta(minutes=2))).all()
  hired4 = Event.query.filter_by(event_type=1).filter(Event.timestamp.between(datetime.now()-timedelta(minutes=4), datetime.now()-timedelta(minutes=3))).all()
  hired5 = Event.query.filter_by(event_type=1).filter(Event.timestamp.between(datetime.now()-timedelta(minutes=5), datetime.now()-timedelta(minutes=4))).all()
  return json.dumps({'h1': len([i.serialize() for i in hired1]),
'h2': len([i.serialize() for i in hired2]),
'h3': len([i.serialize() for i in hired3]),
'h4': len([i.serialize() for i in hired4]),
'h5': len([i.serialize() for i in hired5]),
})

@app.route('/event.json')
def event_data():
  events = Event.query.all()
  return json.dumps([i.serialize() for i in events])

def data_to_display(registry):
  data = {}
  for row in registry:
    user_events = Event.query.filter(Event.phone == row.phone).all()
    data[row.phone] = user_events
  return data


if __name__ == "__main__":
  connect(app)
  print "Connected to DB."

  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
