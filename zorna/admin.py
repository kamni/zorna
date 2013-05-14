from django.contrib.sites.models import Site
from django.contrib import admin

class ZornaAdminSite(admin.AdminSite):
    pass

site = ZornaAdminSite()
site.register(Site)
