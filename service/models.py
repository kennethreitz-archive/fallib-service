import requests
from dynamodb_mapper.model import DynamoDBModel
from werkzeug.security import generate_password_hash, check_password_hash
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError as NotFound
from .utils import render, hash, extract_links

MARKDOWN_URL='http://url2markdown.herokuapp.com/'

class User(DynamoDBModel):
    __table__ = u'fallib-users'
    __hash_key__ = u'username'
    __schema__ = {
        u'username': unicode,
        u'password': unicode,
        u'email': unicode
    }

    @classmethod
    def create(cls, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

        # profile = Document()
        # profile.slug = self.username
        # profile.

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Document(DynamoDBModel):
    __table__ = u'fallib-documents'
    __hash_key__ = u'slug'
    __schema__ = {
        u'slug': unicode,
        u'content': unicode,
        u'archived': bool,
        u'history': unicode,
        u'links': set,
    }
    __defaults__ = {
        u'archived': False,
        u'history': u'da39a3ee5e6b4b0d3255bfef95601890afd80709',
        u'links': set()
    }

    @property
    def text(self):
        return Content.get(self.content).text

    @property
    def html(self):
        return Content.get(self.content).html

    @property
    def owner(self):
        guess = self.slug.split('/')[0]
        try:
            return User.get(guess).username
        except NotFound:
            return None

    def commit_content_hash(self, hash):
        self.content = hash
        self.__append_history(hash)
        self.save()

    def commit_content(self, text):
        content = Content.store(text)
        self.commit_content_hash(content.hash)

        links = URL.store_from_text(text)
        if links:
            self.links = set()
            self.links.update(links)

        self.save()

    @property
    def revisions(self):
        doc = self.__get_history_doc()
        return [i for i in doc.split(',')]

    def __append_history(self, hash):

        revisions = [r for r in revisions if len(r)>2]

        if self.revisions[-1] != hash:
            doc = ','.join(revisions + [hash])

            history = Content.store(doc)
            self.history = history.hash

    def __get_history_doc(self):
        try:
            return Content.get(self.history).text
        except (NotFound, TypeError):
            return u'da39a3ee5e6b4b0d3255bfef95601890afd80709'



class Content(DynamoDBModel):
    __table__ = u'fallib-content'
    __hash_key__ = u'hash'
    __schema__ = {
        u'hash': unicode,
        u'text': unicode,
    }

    @property
    def html(self):
        return render(self.text)

    @classmethod
    def store(cls, text):
        content = cls()
        content.text = text
        content.hash = hash(text)
        content.save()

        return content

class URL(DynamoDBModel):
    __table__ = u'fallib-urls'
    __hash_key__ = u'url'
    __schema__ = {
        u'url': unicode,
        u'content': unicode,
    }

    @classmethod
    def store(cls, url):
        params = {'url': url}
        text = requests.get(MARKDOWN_URL, params=params).text

        content = Content.store(text)

        new_url = cls()
        new_url.url = url
        new_url.content = content.hash
        new_url.save()

        return new_url

    @classmethod
    def store_from_text(cls, text):
        links = extract_links(text)

        for link in links:
            cls.store(link)

        return links


    @property
    def text(self):
        return Content.get(self.content).text

    @classmethod
    def get_or_store(cls, url):
        try:
            return cls.get(url)
        except NotFound:
            return cls.store(url)
