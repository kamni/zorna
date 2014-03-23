import os
from whoosh import index, store, fields
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from django.db.models.signals import post_syncdb
from django.conf import settings

PAGES_WHOOSH_SCHEMA = fields.Schema(title=fields.TEXT(stored=True),
                              content=fields.TEXT(stored=True),
                              url=fields.ID(stored=True, unique=True))

def create_index(sender=None, **kwargs):
    if not os.path.exists(settings.HAYSTACK_WHOOSH_PATH):
        os.mkdir(settings.HAYSTACK_WHOOSH_PATH)
    ix = create_in(settings.HAYSTACK_WHOOSH_PATH, PAGES_WHOOSH_SCHEMA, "ZORNA_PAGES")


post_syncdb.connect(create_index)
