from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import json
import logging
import urllib
from collections import OrderedDict

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from openedx.core.djangoapps.models.course_details import CourseDetails

from courseware.courses import get_permission_for_course_about, get_course_with_access

from edxmako.shortcuts import render_to_response

from xmodule.modulestore.django import modulestore

course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

with modulestore().bulk_operations(course_key):
    permission = get_permission_for_course_about()
    course = get_course_with_access(request.user, permission, course_key)
    course_details = CourseDetails.populate(course)

context = {
    'course_language' : course_details.language
}

return render_to_response('courseware/course_about.html', context)
