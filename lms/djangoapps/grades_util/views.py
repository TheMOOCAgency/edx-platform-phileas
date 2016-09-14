"""
Grades APIs
"""
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.courses import get_course_with_access

from grades_util.scores import has_passed


@login_required
@ensure_csrf_cookie
@require_http_methods(("GET"))
@transaction.non_atomic_requests
def assignment_passing_status(request, course_id, section_id):
    """
    Checks whether the user has 100% in each sub-sections of
    type of the assignment.
    """
    try:
        passed = has_passed(request, course_id, section_id)
    except Exception as e:
        passed = False

    return JsonResponse({
        "passed": passed
    })
