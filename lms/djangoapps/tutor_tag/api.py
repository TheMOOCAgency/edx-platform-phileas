"""
This api returns tutor_tag: true/false based on the discussion_id given in the url

Author : Chintan Joshi
"""
import json

from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore

from courseware.courses import get_course_by_id
from courseware.module_render import get_module_for_descriptor
from courseware.courses import get_course_with_access

from grades_util.scores import has_passed


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
@transaction.non_atomic_requests
def get_api(request, course_id, discussion_id):
    try:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        course = get_course_by_id(course_key)
    except Exception as e:
        return JsonResponse({
            "Error": e.message
        })

    section_id = get_section_id(request,course,discussion_id)
    user_list = json.loads(request.GET.get('users', "[]"))

    data = []
    passed = False
    for username in user_list:
        student = User.objects.get(username=username)
        passed = has_passed(request, course_id, section_id)
        data.append({'username': student.username, 'passed':passed})

    return JsonResponse({
        "data": data
    })

def get_section_id(request, course, discussion_id):
    with modulestore().bulk_operations(course.id):
        course_module = get_module_for_descriptor(
            request.user, request, course, None, course.id, course=course
        )

    for chapter in course_module.get_children():
        for section in chapter.get_children():
            for unit in section.get_children():
                for vertical in unit.get_children():
                    if vertical.category == 'discussion':
                        if vertical.discussion_id == discussion_id:
                            section_id = section.url_name
                            return section_id
