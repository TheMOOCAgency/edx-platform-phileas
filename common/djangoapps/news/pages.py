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
    order_num = NewsPage.objects.all().count()
    page = NewsPage.objects.create(title='Empty', author=author, order_num=order_num)
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
