#!venv/bin/python
import os
from flask import Flask, request
from flask import Flask, render_template, request
from model import connect, db, Registry, Event, Log
from sms import handle_sms_callback

app = Flask(__name__)


@app.route('/api/sms', methods=['GET', 'POST'])
def record_sms():
  return handle_sms_callback(db, request)


@app.route('/map')
def map():
  return render_template('map.html')


@app.route('/')
def home():
  registry = Registry.query.all()
  data = data_to_display(registry)
  return render_template('homepage.html', registry=registry,data=data)


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