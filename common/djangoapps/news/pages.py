"""
Helper for news pages
"""
import json
from news.models import NewsPage

def create_page(author):
    """
    Create page with default values and
    set the author.
    """
    page = NewsPage.objects.create(title='Empty',author=author)
    return page

def save_page(page, values):
    """
    Updates the given page with the given values.
    """
    for attribute, value in values.items():
        setattr(page, attribute, value)
    page.save()

def delete_page(page):
    """
    Delete the page from database permenantly.
    """
    page.delete()
