from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from course_rating.models import CourseRating


@login_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def rate_course(request):
    """
    Description: This view kept for rating the course.

    Request Parameters:
        course_id: course ID for which rating needs to be set.
        stars: float, indicates out of 5 stars

    Returns:
        json response with newly calculated course rating average.

    Assumes the course_id is in a valid format.

    Author: Naresh Makwana
    """
    # Get the parameters from POST
    stars = request.POST.get('stars', 0.0)
    course_id = request.POST.get('course_id')
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

    # save the course ratings
    try:
        course_rating = CourseRating.objects.create(student=request.user, course_id=course_key, stars=stars)
    except IntegrityError:
        pass

    # re-calculate the average course ratings
    avg_ratings = CourseRating.calc_avg_ratings(course_id=course_key)

    # get total number of reviews
    total_reviews = CourseRating.calc_total_reviews(course_id=course_key)

    # return json response
    return JsonResponse({
        'avg_ratings': avg_ratings,
        'total_reviews': total_reviews
    })
