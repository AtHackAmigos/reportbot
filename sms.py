#!venv/bin/python
import twilio.twiml
from model import db, Event, Registry

# TODO: Move to helper class.
def phone_exists(phone):
  return bool(Registry.query.filter_by(phone=phone).first());

def handle_sms_callback(request):
  from_number = request.values.get("From", None)
  if from_number is None:
  	resp = twilio.twiml.Response()
  	resp.message("Sorry, your number is unknown")
  	return str(resp)

  if not phone_exists(from_number):
  	return _register_new_user(from_number)

  resp = twilio.twiml.Response()
  resp.message("You have signed up already. " +
    "Stay tunned for a follow up message next week :)")
  return str(resp)

def _register_new_user(from_number):
  new_phone = Registry(phone=from_number)
  db.session.add(new_phone)
  # Need to commit *before* adding event since Registry is the key.
  db.session.commit()

  db.session.add(Event(phone=from_number, event_type=Event.EVENT_TYPE_HIRE))
  db.session.commit()
  resp = twilio.twiml.Response()
  resp.message("Welcome to ReportBot! (We will keep your number " +
  	from_number + " confidential.)")
  return str(resp)