# -*- coding: utf-8 -*-

from flask import Flask
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg

from .models import Users, Documents, Content

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'


@app.before_request
def before_request():
    """Opens the connection to DynamoDB."""
    g.dynamo_conn = ConnectionBorg()

@app.teardown_request
def teardown_request(exception):
    """Closes the connection to DynamoDB."""
    db = getattr(g, 'dynamo_conn', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run()