#!venv/bin/python
import twilio.twiml
from model import db, last_question_type, phone_exists, Event, Question, Registry


def handle_sms_callback(request):
  from_number = request.values.get("From", None)
  print "DEBUG: request.values: " + request.values
  if from_number is None:
  	resp = twilio.twiml.Response()
  	resp.message("Sorry, your number is unknown")
  	return str(resp)

  if not phone_exists(from_number):
  	return _register_new_user(from_number)

  (is_pulse, answer_value_type) = last_question_type(from_number)

  if is_pulse:
  	_handle_weekly_checkup(from_number)

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

def _handle_weekly_checkup(from_number):
  pass