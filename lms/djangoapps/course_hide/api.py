"""
Api for getting the number of messages posted on the forum by a user

Author: Chintan Joshi
"""
from courseware.courses import get_course_by_id
from django.http import JsonResponse
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import UserProfile

def hide_courses(request):
    courses = request.GET.get('course_list')
    if request.user.is_anonymous():
        return JsonResponse({"Hidden": courses})
    elif request.user.profile.is_manager or request.user.is_staff:
        return JsonResponse({"Hidden":[]})
    else:
        return JsonResponse({"Hidden": courses})
    
