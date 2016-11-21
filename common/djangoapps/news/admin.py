"""
Admin site bindings for news
"""

from django.contrib import admin

from news.models import NewsPage

class NewsPageAdmin(admin.ModelAdmin):
    """Admin panel for the News pages. """
    list_display = (
        'id', 'title', 'visible', 'author', 'created', 'modified',
    )
    search_fields = (
        'id', 'author__username', 'author__email', 'title',
    )

admin.site.register(NewsPage, NewsPageAdmin)
