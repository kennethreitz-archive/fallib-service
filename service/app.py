# -*- coding: utf-8 -*-

from flask import Flask, abort, jsonify, request, redirect, url_for, g
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg

from .models import User, Document, Content, URL, NotFound

app = Flask(__name__)
app.debug = True

def get_or_404(cls, key):
    try:
        return cls.get(key)
    except NotFound:
        abort(404)

@app.route('/')
def hello():
    payload = {
        '/:user': 'JSON representation of a user\'s representation of themself.',
        '/:user/:document': 'JSON representation of a document.',
        '/:user/:document/text': 'Markdown representation of a document.',
        '/:user/:document/html': 'HTML representation of a document.',
        '/archive?q=:url': 'Permanent archive of given URL.',
        '/content/:sha': 'Permanent JSON archive of a given content.',
        '/content/:sha/text': 'Markdown representation of a given content.',
        '/content/:sha/html': 'Permanent HTML representation of a given content.',
    }
    return jsonify(resources=payload)

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
        'links': list(doc.links)
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

@app.route('/content', methods=['POST', 'PUT'])
def add_content():

    assert 'text' in request.form

    text = request.form['text']
    content = Content.store(text)

    return redirect(url_for('get_content', hash=content.hash))


@app.route('/archive')
def archive():

    q = request.args.get('q')
    text = 'text' in request.args

    if not q:
        abort(404)

    url = URL.get_or_store(q)

    if text:
        return url.text

    document = {
        'url': url.url,
        'text': url.text,
        'content': url.content
    }

    return jsonify(url=document)


if __name__ == '__main__':
    app.run()