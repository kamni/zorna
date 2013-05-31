import os
from django.conf import settings


def get_upload_path():
    return settings.ZORNA_UPLOAD_PATH


def get_upload_library():
    path = u"%s/%s" % (settings.ZORNA_UPLOAD_PATH, "library")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_communities():
    path = u"%s/%s" % (get_upload_library(), "communities")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_user(user):
    path = u"%s/%s" % (get_upload_library(), u"U%s" % user.pk)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_avatars():
    return get_upload_path()


def get_upload_articles():
    path = u"%s/%s" % (settings.ZORNA_UPLOAD_PATH, "articles")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_articles_images():
    path = u"%s/%s" % (get_upload_articles(), "images")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_articles_files():
    path = u"%s/%s" % (get_upload_articles(), "files")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_notes_attachments():
    path = u"%s/%s" % (settings.ZORNA_UPLOAD_PATH, "notes")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_forms_attachments():
    path = u"%s/%s" % (settings.ZORNA_UPLOAD_PATH, "forms")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_upload_plugins():
    path = u"%s/%s" % (settings.ZORNA_UPLOAD_PATH, "plugins")
    if not os.path.isdir(path):
        os.makedirs(path)
    return path
