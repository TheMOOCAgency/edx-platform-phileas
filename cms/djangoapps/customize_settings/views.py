from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from contentstore.views.course import get_course_and_check_access

from xmodule.modulestore.django import modulestore

from models.settings.course_metadata import CourseMetadata

@csrf_exempt
def customize_settings(request,course_key_string):

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_key_string)
    with modulestore().bulk_operations(course_key):
        course_module = get_course_and_check_access(course_key, request.user)
        additional_info = {
        'is_new': request.POST.get('is_new', False),
        'invitation_only': request.POST.get('invitation_only', False),
        'manager_only': request.POST.get('manager_only', False)
        }
        CourseMetadata.update_from_dict(additional_info, course_module, request.user)
        return JsonResponse({'data':'data'})