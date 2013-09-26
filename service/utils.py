import hashlib
from markdown import markdown

def render(text):
    return unicode(markdown(text))

def hash(text):
    return unicode(hashlib.sha1(text).hexdigest())

