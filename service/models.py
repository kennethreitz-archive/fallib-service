from dynamodb_mapper.model import DynamoDBModel
from werkzeug.security import generate_password_hash, check_password_hash
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError as NotFound
from .utils import render, hash

class Users(DynamoDBModel):
    __table__ = u'fallib-users'
    __hash_key__ = u'username'
    __schema__ = {
        u'username': unicode,
        u'password': str,
        u'email': unicode
    }

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Documents(DynamoDBModel):
    __table__ = u'fallib-documents'
    __hash_key__ = u'slug'
    __schema__ = {
        u'slug': unicode,
        u'content': unicode,
        u'archived': bool,
        u'history': unicode,
    }

    def commit_content_hash(self, hash):
        self.__append_history(content.hash)
        self.save()

    def commit_content(self, text):
        content = Content.store(doc)
        self.commit_content_hash(content.hash)

    @property
    def revisions(self):
        doc = self.__get_history_doc()
        return (i for i in doc.split())

    def __append_history(self, hash):

        doc = __get_history_doc()
        doc = ','.join([doc, hash])

        history = Content.store(doc)
        self.history = history.hash


    def __get_history_doc(self):
        try:
            return Content.get(self.history)
        except NotFound:
            return 'da39a3ee5e6b4b0d3255bfef95601890afd80709'


class Content(DynamoDBModel):
    __table__ = u'fallib-content'
    __hash_key__ = u'hash'
    __schema__ = {
        u'hash': unicode,
        u'text': unicode,
    }

    @classmethod
    def store(cls, text):
        content = cls()
        content.text = text
        content.hash = hash(text)
        content.save()

        return content