# -*- coding: utf-8 -*-

from flask import Flask, abort, jsonify, g
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg

from .models import User, Document, Content, NotFound

app = Flask(__name__)

def get_or_404(cls, key):
    try:
        return cls.get(key)
    except NotFound:
        abort(404)

@app.route('/')
def hello():
    return 'Hello World!'

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error={'status': 'Not found.', 'code': '404'}), 404


@app.route('/<path:slug>')
def get_document(slug):

    doc = get_or_404(Document, slug)

    document = {
        'slug': doc.slug,
        'owner': doc.owner,
        'text': doc.text,
        'content': doc.content,
        'history': doc.revisions,
    }

    return jsonify(document=document)

@app.route('/<path:slug>/text')
def get_document_text(slug):

    doc = get_or_404(Document, slug)
    return doc.text

@app.route('/<path:slug>/html')
def get_document_html(slug):

    doc = get_or_404(Document, slug)
    return doc.html

@app.route('/content/<hash>')
def get_content(hash):

    doc = get_or_404(Content, hash)

    document = {
        'hash': doc.hash,
        'text': doc.text,
    }

    return jsonify(content=document)

@app.route('/content/<hash>/text')
def get_content_text(hash):

    doc = get_or_404(Content, hash)
    return doc.text

@app.route('/content/<hash>/html')
def get_content_html(hash):

    doc = get_or_404(Content, hash)
    return doc.html

if __name__ == '__main__':
    app.run()