from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from course_progress.models import StudentCourseProgress


@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_overall_course_progress(request):
    """
    Description: This view kept for fetching the overall course progress.

    Request Parameters:
        course_id: course ID for which progress needs to be calculated.
        student_id: Student for which progress needs to be calculated.

    Returns:
        json response

    Assumes the course_id is in a valid format.

    Author: Naresh Makwana
    """
    overall_progress = 0

    course_id = request.GET.get('course_id')

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    try:
        student_course_progress = StudentCourseProgress.objects.get(student=request.user.id, course_id=course_key)
        overall_progress = student_course_progress.overall_progress
    except StudentCourseProgress.DoesNotExist:
        pass

    return JsonResponse({'overall_progress': overall_progress})
