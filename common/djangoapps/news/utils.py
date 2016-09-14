"""
Common utility functions useful throughout the contentstore
"""

import logging

from django.conf import settings


log = logging.getLogger(__name__)


def get_lms_link_for_news(preview=False):
    """
    Returns an LMS link to the news.

    :param preview: True if the preview version of LMS should be returned. Default value is false.
    """
    if settings.LMS_BASE is None:
        return None

    if preview:
        lms_base = settings.FEATURES.get('PREVIEW_LMS_BASE')
    else:
        lms_base = settings.LMS_BASE

    return u"//{lms_base}/news/".format(
        lms_base=lms_base
    )
