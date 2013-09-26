# -*- coding: utf-8 -*-

from flask import Flask, abort, jsonify, g
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg

from .models import User, Document, Content

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'


# @app.before_request
# def before_request():
#     """Opens the connection to DynamoDB."""
#     g.dynamo_conn = ConnectionBorg()

@app.route('/<path:slug>')
def get_document(slug):
    doc = Document.get(slug)

    document = {
        'slug': doc.slug,
        'owner': doc.owner,
        'text': doc.text,
        'content': doc.content,
        'history': doc.revisions,
    }

    return jsonify(document=document)


getattr


if __name__ == '__main__':
    app.run()