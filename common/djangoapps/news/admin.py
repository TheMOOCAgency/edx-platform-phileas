"""
Admin site bindings for news
"""

from django.contrib import admin

from news.models import NewsPage

admin.site.register(NewsPage)
