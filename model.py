import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

db = SQLAlchemy()

DB_URL = os.environ.get("DB_URL", "")


class Registry(db.Model):
  """Data model for Registry."""
  __tablename__ = "registry"

  phone = db.Column(db.String(32), primary_key=True)

  def serialize(self):
    return {
        'phone': self.phone,
    }

  def __repr__(self):
    return "<Registry phone=%s>" % self.phone


class Event(db.Model):
  """Data model for Event."""
  __tablename__ = "event"
  EVENT_TYPE_UNKNOWN = 0
  EVENT_TYPE_HIRE = 1
  EVENT_TYPE_PULSE = 2
  EVENT_TYPE_LOST = 3
  EVENT_TYPE_QUESTION = 4
  EVENT_TYPE_ANSWER = 5

  event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  event_type = db.Column(db.Integer)
  timestamp = db.Column(db.DateTime, server_default=db.func.now())
  phone = db.Column(db.String(32), db.ForeignKey("registry.phone"))
  data = db.Column(db.Integer)
  log = db.Column(db.Integer, db.ForeignKey("log.log_id"))

  def serialize(self):
    return {
        'event_type': str(self.event_type),
        'timestamp': str(self.timestamp),
        'phone': self.phone,
        'data': str(self.data),
    }

  def __repr__(self):
    return "<Event event_id=%s, event_type=%s, timestamp=%s, phone=%s, data=%s, log=%s>" % (
        self.event_id,
        self.event_type,
        self.timestamp,
        self.phone,
        self.data,
        self.log)


class Log(db.Model):
  """Data model for Log."""
  __tablename__ = "log"
  log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  text = db.Column(db.String(128))

  def __repr__(self):
    return "<Log log_id=%d, text=%s>" % (self.log_id, self.text)


class Question(db.Model):
  """Data model for Question."""
  __tablename__ = "question"

  VALUE_TYPE_UNKNOWN = 0
  VALUE_TYPE_STRING = 1
  VALUE_TYPE_INTEGER = 2
  VALUE_TYPE_MC_2 = 3
  VALUE_TYPE_MC_3 = 4
  VALUE_TYPE_MC_4 = 5
  VALUE_TYPE_MC_5 = 6

  question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  text = db.Column(db.String(256))
  value_type = db.Column(db.Integer)

  def __repr__(self):
    return "<Question question_id=%d, text=%s, value_type=%d>" % (self.question_id, self.text, self.value_type)

## Debug functions. ##

def connect(app):
  # Connect to database
  app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
  app.config['SQLALCHEMY_ECHO'] = True
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  db.app = app
  db.init_app(app)


def print_tables():
  print "== table registry ==="
  for phone in Registry.query.all():
    print phone
  print "== table question ==="
  for question in Question.query.all():
    print question
  print "== table events ==="
  for event in Event.query.all():
    print event
  print "== table log ==="
  for log in Log.query.all():
    print log


def setup():
  # Setup schema.
  db.create_all()
  setup_questions()

def setup_questions():
  # Setup question table.
  questions = [
      (Question.VALUE_TYPE_MC_2,
       "Are you still in touch with the worker?"),
      (Question.VALUE_TYPE_MC_2,
       "Welcome to Reportbot. We have some questions, Press 1 to continue if interested, otherwise we will send you a weekly check up next week."),
      (Question.VALUE_TYPE_MC_3,
       "How are you related to the worker? Press 1 for Parents, 2 for Family, 3 for Friend?"),
      (Question.VALUE_TYPE_MC_5,
       "Who referred the worker to this oppty? Press 1 for Friend, 2 for Family, 3 for Community Leader, 4 for Recruiter, 5 for Other?"),
      (Question.VALUE_TYPE_STRING,
       "What is the recruiter's phone number? Enter 0 if not sure"),
      (Question.VALUE_TYPE_STRING,
       "Where are they going to work? Enter city or country"),
      (Question.VALUE_TYPE_MC_3,
       "What type of job will they do? Press 1 for Domestic Service, 2 for Factory, 3 for Farm/Fishing, 4 for Other"),
      (Question.VALUE_TYPE_MC_3,
       "How old is the worker?"),
      (Question.VALUE_TYPE_MC_3,
       "What is the worker's gender? Press 1 for Male, 2 for Female"),
      (Question.VALUE_TYPE_MC_3,
       "Can we follow-up again? Press 1 for Yes, 2 for No"),
  ]

  for q in questions:
    db.session.add(Question(text=q[1], value_type=q[0]))
  db.session.commit()

def clear_tables():
  meta = db.metadata
  for table in reversed(meta.sorted_tables):
    print 'Clear table %s' % table
    db.session.execute(table.delete())
  db.session.commit()


def tear_down():
  clear_tables()
  db.reflect()
  db.drop_all()


def create_mock_dataset():
  p0 = Registry(phone="000-000-0000")
  p1 = Registry(phone="000-000-0001")
  p2 = Registry(phone="000-000-0002")
  db.session.add(p0)
  db.session.add(p1)
  db.session.add(p2)
  db.session.commit()
  db.session.add(Event(phone=p0.phone, event_type=Event.EVENT_TYPE_HIRE))
  db.session.add(Event(phone=p1.phone, event_type=Event.EVENT_TYPE_HIRE))
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_HIRE))
  db.session.add(Event(phone=p0.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p1.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p0.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p1.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.add(Event(phone=p0.phone, event_type=Event.EVENT_TYPE_LOST))
  db.session.add(Event(phone=p1.phone, event_type=Event.EVENT_TYPE_PULSE))
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_QUESTION, data=7))
  l = Log(text="14")
  db.session.add(l)
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_ANSWER, data=14, log=l.log_id))
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_QUESTION, data=5))
  l = Log(text="Mountain View, CA")
  db.session.add(l)
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_ANSWER, data=1, log=l.log_id))
  db.session.commit()


def phone_exists(phone):
  return bool(Registry.query.filter_by(phone=phone).first());


def send_pulse():
  lost_phones_query = Event.query.filter_by(event_type=Event.EVENT_TYPE_LOST).order_by(Event.phone).all()
  lost_phones = {l.phone for l in lost_phones_query}
  all_phones_query = Event.query.all()
  all_phones = {a.phone for a in all_phones_query}
  send_phones = sorted(all_phones - lost_phones)
  for phone in send_phones:
    db.session.add(Event(phone=phone, event_type=Event.EVENT_TYPE_QUESTION, data=1))
  db.session.commit()
  msg = Question.query.filter_by(question_id=1).first().text
  return send_phones, msg


def phone_exists(phone):
  return bool(Registry.query.filter_by(phone=phone).first());


def last_question_type(phone):
  # Return (is_pulse, answer_value_type) tuple
  event_query = Event.query.filter_by(phone=phone).order_by(desc(Event.timestamp)).first()
  if not event_query or event_query.event_type != Event.EVENT_TYPE_QUESTION:
    return (False, Question.VALUE_TYPE_UNKNOWN)
  question_query = Question.query.filter_by(question_id=event_query.data).first()
  return bool(question_query.question_id == 1), question_query.value_type


def welcome(phone):
  db.session.add(Event(phone=phone, event_type=Event.EVENT_TYPE_QUESTION, data=2))
  db.session.commit()

# def next_question(phone):
#   event_query = Event.query.filter_by(phone=phone, event_type=Event.EVENT_TYPE_QUESTION).order_by(desc(Event.timestamp)).first()
#   if not event_query or event_query.data == 1:
#     return None
#   if event_query.data == 2:
#     event_a_query = Event.query.filter_by(phone=phone, event_type=Event.EVENT_TYPE_ANSWER).order_by(desc(Event.timestamp)).first()
#     if not event_a_query or event_a_query.timestamp < event_query.timestamp:
#       # No answer or answer pre-dates question.
#       return None
#   if event_query.data < 9:
#     question_query = Question.query.filter_by(question_id=event_query.data+1).first()
#     db.session.add(Event(phone=phone, event_type=Event.EVENT_TYPE_QUESTION, data=event_query.data+1))
#     return question_query.text
#   return None

def main(argv):
  if not len(argv):
    print "Specify command: "
    print "  setup_table"
    print "  create_mock"
    print "  print_tables"
    print "  send_pulse"
    print "  clear_tables"
    print "  clean"
    print "  phone_exists"
    print "  last_question_type <phone>"

  cmd = argv[1];

  print "Connect..."
  connect(Flask("test-bot"))
  print "Connected to DB."

  if cmd == "setup":
    setup()
    print "SetUp."
  elif cmd == "create_mock":
    create_mock_dataset()
    print "created mock data."
  elif cmd == "print_tables":
    print_tables()
  elif cmd == "clear_tables":
    clear_tables()
  elif cmd == "send_pulse":
    print send_pulse()
  elif cmd == "last_question_type":
    if len(argv) < 3:
      print "Missing argument"
    print "Last question asked has type: %s, %s" % last_question_type(argv[2])
  elif cmd == "phone_exists":
    print "Phone %s in the registry? %s" % (argv[2], phone_exists(argv[2]))
  elif cmd == "clean":
    print "torn down."
    tear_down()
  else:
    print "Unknow command: ", cmd


if __name__ == "__main__":
  main(sys.argv)
