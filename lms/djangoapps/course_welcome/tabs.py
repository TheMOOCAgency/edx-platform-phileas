"""
This module is kept for adding new custom tabs.

Author: Naresh Makwana
"""
from django.utils.translation import ugettext_noop
from courseware.tabs import EnrolledTab


class CourseWelcomeTab(EnrolledTab):
    """
    The course welcome view.
    """
    type = 'course_welcome'
    title = ugettext_noop('Welcome')
    priority = 1
    view_name = 'welcome'
    tab_id = 'welcome'
    is_movable = False
    is_default = True

    @classmethod
    def is_enabled(cls, course, user=None):
        return True
