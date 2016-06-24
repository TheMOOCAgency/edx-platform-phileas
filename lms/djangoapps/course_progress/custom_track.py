import json

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx.keys import CourseKey, UsageKey
from opaque_keys import InvalidKeyError

from course_progress.models import StudentHistory


@login_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def track_html_component(request):
    """
    Description: This view kept for tracking the HTML
    component view, for the given student in a particular course.

    Author: Naresh Makwana
    """
    student = request.user
    course_id = request.POST.get('course_id')
    usage_ids_json = request.POST.get('usage_ids')
    usage_ids = json.loads(usage_ids_json)

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    for usage_id in usage_ids:
        try:
            # Returns a subclass of UsageKey, depending on what's being parsed.
            usage_key = UsageKey.from_string(usage_id).map_into_course(course_key)
        except InvalidKeyError:
            continue

        StudentHistory.objects.get_or_create(
            student=student,
            course_id=course_key,
            module_state_key=usage_key,
            module_type='html',
            done='f',
        )

    return JsonResponse({'success': True})


def track_custom_event(student, course_key, instance):
    """
    Stores the courseware student history that is not by default tracked.
    i.e. problem hints, LTI grade events, etc.

    Author: Naresh Makwana
    """
    StudentHistory.objects.get_or_create(
        student=student,
        course_id=course_key,
        module_state_key=instance.location,
        module_type=instance.category,
        done='f',
    )