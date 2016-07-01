"""
Course rating helpers
"""
from course_rating.models import CourseRating


def inject_course_ratings_into_context(context, user, course_key):
    """
    Set params to view context based on course_key and user

    :param context: view context
    :type context: dict
    :param course_key: SlashSeparatedCourseKey instance
    :type course_key: SlashSeparatedCourseKey

    Author: Naresh Makwana
    """
    context['total_reviews'] = CourseRating.calc_total_reviews(course_id=course_key)
    context['avg_ratings'] = CourseRating.calc_avg_ratings(course_id=course_key)
    context['can_rate'] = context['registered'] and \
        not CourseRating.has_rated(student_id=user.id, course_id=course_key)
