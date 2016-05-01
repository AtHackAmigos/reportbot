#!venv/bin/python

import os
import twilio.twiml
from twilio.rest import TwilioRestClient
from model import db, last_question_type, phone_exists, Event, Question, Registry

ACCOUNT_SID = os.environ.get("ACCOUNT_SID", "")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

def send_sms():
  print "DEBUG: sending sms"
  message = client.messages.create(to="+14048278486", from_="+17293994804", body="Hello there!")
  print "DEBUG: %s" % message

def handle_sms_callback(request):
  from_number = request.values.get("From", None)
  if from_number is None:
    resp = twilio.twiml.Response()
    resp.message("Sorry, your number is unknown")
    return str(resp)

  if not phone_exists(from_number):
    return _register_new_user(from_number)

  (is_pulse, answer_value_type) = last_question_type(from_number)

  if is_pulse:
    if not _handle_weekly_checkup(request, from_number):
      resp = twilio.twiml.Response()
      resp.message("Sorry, invalid response. Please try again.")
      return str(resp)

  if answer_value_type == Question.VALUE_TYPE_UNKNOWN:
    resp = twilio.twiml.Response()
    resp.message("You have signed up already. Stay tunned for a follow up message next week :)")
    return str(resp)


def _register_new_user(from_number):
  new_phone = Registry(phone=from_number)
  db.session.add(new_phone)
  # Need to commit *before* adding event since Registry is the key.
  db.session.commit()

  db.session.add(Event(phone=from_number, event_type=Event.EVENT_TYPE_HIRE))
  db.session.commit()
  resp = twilio.twiml.Response()
  resp.message("Welcome to ReportBot! (We will keep your number " + from_number + " confidential.)")
  return str(resp)

def _handle_weekly_checkup(request, from_number):
  body = request.values.get("Body", None)
  if body == "1":
    db.session.add(Event(phone=from_number, event_type=Event.EVENT_TYPE_PULSE))
    return True
  elif body == "2":
    db.session.add(Event(phone=from_number, event_type=Event.EVENT_TYPE_LOST))
    return True
  else:
    return False