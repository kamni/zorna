import django.dispatch
from django.dispatch import receiver
import HTMLParser
from BeautifulSoup import BeautifulSoup
from whoosh.index import open_dir
from django.conf import settings

zorna_page_save  = django.dispatch.Signal(providing_args=[])


@receiver(zorna_page_save, sender=None)
def pages_update_index(sender, **kwargs):
    pars = HTMLParser.HTMLParser()
    text = pars.unescape(kwargs['content'])
    text = ''.join( BeautifulSoup( text ).findAll( text = True ) )

    ix = open_dir(settings.HAYSTACK_WHOOSH_PATH, indexname="ZORNA_PAGES")
    writer = ix.writer()
    if kwargs['created']:
        writer.add_document(title=unicode(kwargs['title']), content=text,
                                    url=unicode(kwargs['url']))
        writer.commit()
    else:
        writer.update_document(title=unicode(kwargs['title']), content=text,
                                    url=unicode(kwargs['url']))
        writer.commit()
