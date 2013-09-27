# -*- coding: utf-8 -*-

from functools import wraps
from flask import Flask, abort, jsonify, request, redirect, url_for, g
from flask import Response
from dynamodb_mapper.model import DynamoDBModel, ConnectionBorg
from .models import User, Document, Content, URL, NotFound


app = Flask(__name__)
app.debug = True

def get_or_404(cls, key):
    try:
        return cls.get(key)
    except NotFound:
        abort(404)

def check_auth(username, password):
    try:
        user = User.get(username)
    except NotFound:
        return False

    ok = user.check_password(password)

    if ok:
        g.user = username
    else:
        g.user = None

    return ok

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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
def error_404(e):
    return jsonify(error={'status': 'WHAT IS THIS!?', 'code': '404'}), 404

@app.errorhandler(403)
def error_403(e):
    return jsonify(error={'status': 'FORBIDDEN!', 'code': '403'}), 403

@app.errorhandler(401)
def error_401(e):
    return jsonify(error={'status': 'STOP RIGHT THERE!', 'code': '401'}), 401

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


@app.route('/<path:slug>', methods=['PUT', 'POST'])
@protected
def post_document(slug):

    text = request.form['text']

    try:
        doc = Document.get(slug)
    except NotFound:
        doc = Document()
        doc.slug = slug

    if not g.user == doc.owner:
        abort(403)

    doc.commit_content(text)

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
    return doc.text, 200, {'Content-Type': 'text/x-markdown; charset=UTF-8'}

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
    return doc.text, 200, {'Content-Type': 'text/x-markdown; charset=UTF-8'}

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
        return url.text, 200, {'Content-Type': 'text/x-markdown; charset=UTF-8'}

    document = {
        'url': url.url,
        'text': url.text,
        'content': url.content
    }

    return jsonify(url=document)


if __name__ == '__main__':
    app.run()