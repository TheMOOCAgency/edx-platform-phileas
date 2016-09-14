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

from grades_util.scores import has_passed


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
        passed = has_passed(request, course_id, section_id)
        data.append({'username': student.username, 'passed':passed})

    return Response(
        data={
        "data":data
    })

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