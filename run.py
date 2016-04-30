#!venv/bin/python
from twilio.rest import TwilioRestClient
import twilio
import twilio.twiml
from flask import Flask, request, redirect
from app import app
app.run(debug=True)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond with a simple text message."""

    resp = twilio.twiml.Response()
    resp.message("Hello! This is a test msg.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
