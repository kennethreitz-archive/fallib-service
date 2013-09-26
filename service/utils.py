import hashlib
from markdown import markdown

def render(text):
    return str(markdown(text))

def hash(text):
    return str(hashlib.sha1(text).hexdigest())

