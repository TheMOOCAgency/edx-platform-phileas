"""
Common utility functions useful throughout the contentstore
"""

import logging

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


log = logging.getLogger(__name__)


def get_lms_base(preview=False):
    if settings.LMS_BASE is None:
        return None

    if preview:
        lms_base = settings.FEATURES.get('PREVIEW_LMS_BASE')
    else:
        lms_base = settings.LMS_BASE

    return lms_base

def get_lms_link_for_news(preview=False):
    """
    Returns an LMS link to the news.

    :param preview: True if the preview version of LMS should be returned. Default value is false.
    """
    lms_base = get_lms_base(preview)

    return u"//{lms_base}/news/".format(
        lms_base=lms_base
    )

def get_default_jacket_url():
    return staticfiles_storage.url('images/default_jacket.jpg')

def get_media_link_for_jacket(page):
    media_link = get_default_jacket_url()
    jacket = page.jacket.url if page.jacket and 'undefined' not in page.jacket.url else ''
    if jacket:
        lms_base = get_lms_base()

        media_link = u"//{lms_base}{jacket}".format(
            lms_base=lms_base,
            jacket=jacket
        )

    return media_link
