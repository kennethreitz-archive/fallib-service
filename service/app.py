# -*- coding: utf-8 -*-

from flask import Flask, abort, jsonify, g
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg

from .models import User, Document, Content, NotFound

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error={'status': 'Not found.', 'code': '404'}), 404


@app.route('/<path:slug>')
def get_document(slug):

    try:
        doc = Document.get(slug)
    except NotFound:
        abort(404)

    document = {
        'slug': doc.slug,
        'owner': doc.owner,
        'text': doc.text,
        'content': doc.content,
        'history': doc.revisions,
    }

    return jsonify(document=document)


if __name__ == '__main__':
    app.run()