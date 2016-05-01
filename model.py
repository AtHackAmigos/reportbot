import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DB_URL = os.environ.get("DB_URL", "")


class Registry(db.Model):
  """Data model for Registry."""
  __tablename__ = "registry"

  phone = db.Column(db.String(32), primary_key=True)

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
  db.session.add(Question(text="Are you still in touch with your daughter?", value_type=Question.VALUE_TYPE_MC_2))
  db.session.add(Question(text="Where does your daughter work?", value_type=Question.VALUE_TYPE_STRING))
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_QUESTION, data=1))
  l = Log(text="1")
  db.session.add(l)
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_ANSWER, data=1, log=l.log_id))
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_QUESTION, data=2))
  l = Log(text="Mountain View, CA")
  db.session.add(l)
  db.session.commit()
  db.session.add(Event(phone=p2.phone, event_type=Event.EVENT_TYPE_ANSWER, data=1, log=l.log_id))
  db.session.commit()


def phone_exists(phone):
  return bool(Registry.query.filter_by(phone=phone).first());

def main(argv):
  if not len(argv):
    print "Specify command: setup_table, create_mock, print_tables, clear_tables, clean, phone_exists"

  cmd = argv[1];

  print "Connect..."
  connect(Flask("test-bot"))
  print "Connected to DB."

  if cmd == "setup_table":
    db.create_all()
    print "Created schema."
  elif cmd == "create_mock":
    create_mock_dataset()
    print "created mock data."
  elif cmd == "print_tables":
    print_tables()
  elif cmd == "clear_tables":
    clear_tables()
  elif cmd == "phone_exists":
    print "Phone %s in the registry? %s" % (argv[2], phone_exists(argv[2]))
  elif cmd == "clean":
    print "torn down."
    tear_down()
  else:
    print "Unknow command: ", cmd


if __name__ == "__main__":
  main(sys.argv)
