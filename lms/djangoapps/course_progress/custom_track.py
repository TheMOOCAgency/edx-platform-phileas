import json

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx.keys import UsageKey
from opaque_keys import InvalidKeyError

from course_progress.progress import update_course_progress


@login_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def track_html_component(request):
    """
    Description: This view kept for tracking the HTML
    component view, for the given student in a particular course.

    Author: Naresh Makwana
    """
    course_id = request.POST.get('course_id')
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    usage_ids_json = request.POST.get('usage_ids')
    usage_ids = json.loads(usage_ids_json)
    usage_keys = []
    for usage_id in usage_ids:
        try:
            # Returns a subclass of UsageKey, depending on what's being parsed.
            usage_key = UsageKey.from_string(usage_id).map_into_course(course_key)
            usage_keys.append(usage_key)
        except InvalidKeyError:
            continue

    # update the course progress
    update_course_progress(request.user, course_key, 'html', usage_keys)

    return JsonResponse({'success': True})
