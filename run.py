#!venv/bin/python
import os
from flask import Flask, request
from twilio.util import TwilioCapability
import twilio.twiml
from flask import Flask, render_template, request
from model import connect, db, Registry, Event, Log

app = Flask(__name__)


@app.route('/api/sms', methods=['GET', 'POST'])
def record_sms():
  resp = twilio.twiml.Response()
  from_number = request.values.get("From", None)
  if from_number is None:
    resp.message("Sorry, your number is unknown")
    return str(resp)

  if not phone_exists(from_number):
    new_phone = Registry(phone=from_number)
    db.session.add(new_phone)
    db.session.commit()
    db.session.add(Event(phone=from_number, event_type=Event.EVENT_TYPE_HIRE))
    db.session.commit()
    resp.message("Welcome to ReportBot! (We will keep your number " +
      from_number + " confidential.)")
    return str(resp)

  resp.message("You have signed up already. " +
    "Stay tunned for a follow up message next week :)")
  return str(resp)


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
