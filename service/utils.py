import os
import re
import hashlib

from markdown import markdown

GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def render(text):
    return unicode(markdown(text))

def hash(text):
    return unicode(hashlib.sha1(text.encode('utf-8')).hexdigest())

def extract_links(text):

    links = set()
    for url in(mgroups[0] for mgroups in GRUBER_URLINTEXT_PAT.findall(text)):
        if url.startswith('http'):
            links.add(url)
    return list(links)