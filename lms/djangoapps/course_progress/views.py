from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse

from edxmako.shortcuts import render_to_response
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore

from course_progress.models import StudentCourseProgress
from course_progress.helpers import get_overall_progress


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
    course_id = request.GET.get('course_id')
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    overall_progress = get_overall_progress(request.user.id, course_key)

    return JsonResponse({'overall_progress': overall_progress})

@login_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_completion_status(request):
    """
    Description: To check completion status of the section/chapter.

    Request Parameters:
        course_id: course ID string.

    Returns:
        json response

    Assumes the course_id is in a valid format.

    Author: Naresh Makwana
    """
    # Set initial value to progress
    progress= {}
    completion_status = {}

    # Get course id and convert it to course key
    course_id = request.GET.get('course_id')
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    # Get the student course completion progress
    try:
        student_course_progress = StudentCourseProgress.objects.get(student=request.user.id, course_id=course_key)
        progress = student_course_progress.progress
    except StudentCourseProgress.DoesNotExist:
        pass

    # Prepare completion status dictionary
    chapters_completed = []
    sections_completed = []

    course_usage_key = modulestore().make_course_usage_key(course_key)
    course_block = progress.get(str(course_usage_key), {})
    for chapter_id in course_block.get('children', []):
        if progress[chapter_id]['progress'] == 100:
            chapters_completed.append(progress[chapter_id]['display_name'])
        else:
            chapter_progress = progress.get(chapter_id, {})
            for section_id in chapter_progress.get('children', []):
                if progress[section_id]['progress'] == 100:
                    section_url_name = section_id.split('@')[-1]
                    sections_completed.append(section_url_name)

    completion_status.update({
        'chapters_completed': chapters_completed,
        'sections_completed': sections_completed
    })

    # Return the JSON resposne
    return JsonResponse({'completion_status': completion_status})
