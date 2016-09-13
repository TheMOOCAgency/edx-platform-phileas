"""
Student pass fail info api
"""
from xmodule.modulestore.django import modulestore
from courseware.model_data import FieldDataCache, ScoresClient
from util.db import outer_atomic
from courseware import grades
from django.db import transaction
from student.models import User 

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from edx_rest_framework_extensions.authentication import JwtAuthentication

from openedx.core.lib.api.view_utils import view_auth_classes
from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.courses import get_course_with_access

@view_auth_classes()
@transaction.non_atomic_requests
@api_view()
def get_api(request,course_id,section_id):
    """
    **Example Requests**

        GET: /pass_fail/course_id/section_id

    **Returns**

        passed: true  (if the student has passed the section)

        passed: false (if the student has not passed)
    """
    student = request.user
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_with_access(student, 'load', course_key, depth=None)
    with outer_atomic():
        field_data_cache = grades.field_data_cache_for_grading(course, student)
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    courseware_summary = grades.progress_summary(
        student, request, course, field_data_cache=field_data_cache, scores_client=scores_client
    )

    # find the passing grade for the course
    nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) * 100 if nonzero_cutoffs else 0

    chapters = []
    passed = False
    for chapter in courseware_summary:
        if not chapter['display_name'] == "hidden":
            for section in chapter['sections']:
                if section['url_name'] == section_id:
                    earned = section['section_total'].earned
                    total = section['section_total'].possible
                    percentage = earned * 100 / total if earned > 0 and total > 0 else 0
                    passed = success_cutoff and percentage >= success_cutoff

                    break

    return Response(
        data={
        "passed":passed
    })
