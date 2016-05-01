#!venv/bin/python
import twilio.twiml

# TODO: Move to helper class.
def phone_exists(phone):
  from model import Registry
  return bool(Registry.query.filter_by(phone=phone).first());

def record_sms(db, request):
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