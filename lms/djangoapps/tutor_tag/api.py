"""
This api returns tutor_tag: true/false based on the discussion_id given in the url

Author : Chintan Joshi
"""

from rest_framework.response import Response
from openedx.core.lib.api.view_utils import view_auth_classes
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from lms.lib.comment_client.thread import Thread
from courseware.courses import get_course_by_id
from student.models import User
from courseware.module_render import get_module_for_descriptor

from xmodule.modulestore.django import modulestore
from courseware.model_data import ScoresClient
from util.db import outer_atomic
from courseware import grades
from django.db import transaction

from rest_framework.decorators import api_view
from edx_rest_framework_extensions.authentication import JwtAuthentication

from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)



@view_auth_classes()
@transaction.non_atomic_requests
@api_view()
def get_api(request,course_id,discussion_id):
    try:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    except Exception as e:
        return Resposne(
            data={
            "Error": e.message
        })
    passed = False
    course = get_course_by_id(course_key)
    section_id = get_section_id(request,course,discussion_id)
    user_list = dict(request.GET)['users[]']
    data = []
    for username in user_list:
        student = User.objects.get(username=username)
        tutor_Tag = get_tutor_tag(student,request,course,section_id)
        data.append(tutor_Tag)

    return Response(
        data={

        "data":data
    })


def get_tutor_tag(student,request,course,section_id):
    chapters = []
    section_index = 0
    passed = False
    with outer_atomic():
        field_data_cache = grades.field_data_cache_for_grading(course, student)
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    courseware_summary = grades.progress_summary(
        student, request, course, field_data_cache=field_data_cache, scores_client=scores_client
    )

    # find the passing grade for the course
    nonzero_cutoffs = [cutoff for cutoff in course.grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) * 100 if nonzero_cutoffs else 0

    for chapter in courseware_summary:
        if not chapter['display_name'] == "hidden":
            for section in chapter['sections']:
                if section['url_name'] == section_id:
                    section_index += 1
                    earned = section['section_total'].earned
                    total = section['section_total'].possible
                    percentage = earned * 100 / total if earned > 0 and total > 0 else 0
                    passed = success_cutoff and percentage >= success_cutoff
                    break

    return {'username': student.username,'passed':passed}

def get_section_id(request,course,discussion_id):
    with modulestore().bulk_operations(course.id):
        course_module = get_module_for_descriptor(
            request.user, request, course, None, course.id, course=course
        )
        if course_module is None:
            return Response(
                data={
                "Error":"User is not allowed to do the operation"
            })

    for chapter in course_module.get_children():
        for section in chapter.get_children():
            for unit in section.get_children():
                for vertical in unit.get_children():
                    if vertical.category == 'discussion':
                        if vertical.discussion_id == discussion_id:
                            section_id = section.url_name
                            return section_id