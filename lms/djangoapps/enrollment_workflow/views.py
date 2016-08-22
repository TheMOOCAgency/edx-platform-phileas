"""
View which gets the information of user and sends mail to the given email in lms.env.json

Author: Chintan Joshi
"""
from django.core import mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from edxmako.shortcuts import render_to_string

from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from course_modes.models import CourseMode

from student.models import CourseEnrollment, User

from .models import RequestEnroll

@require_POST
def workflow(request):
    user = request.user
    if user.is_authenticated():
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        except Exception as e:
            return JsonResponse({"Error": e.message})

        course = CourseOverview.get_from_id(course_key)
        context = {
                'site':settings.SITE_NAME,
                'student':user,
                'course_id':course.id,
                'course_name':course.display_name
        }
        subject = "Enrollment Request for '{}' ({}) course".format(course.display_name,course.id)
        message = render_to_string('emails/enrollment_request.txt', context)
        from_address = user.email
        dest_addr = settings.FEATURES.get('ENROLLMENT_REQUEST_EMAIL')
        student_request = RequestEnroll(student=request.user,course_id=course.id,enrollment_status='requested')
        student_request.save()
        try:
            mail.send_mail(subject, message, from_address, [dest_addr], fail_silently=False)
        except Exception as e:
            return JsonResponse(
                {
                "Error": e.message
            })

        return JsonResponse(
            {
            "Success":True 
        })

    else:
        return JsonResponse({'Error':'User not authentictated'})

def granted(request,course_id,student_id):
    user = request.user
    if user.is_superuser:
        try:
            student = User.objects.get(id=student_id)
        except Exception as e:
            return JsonResponse({"Error":e.message})
        try:
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        except Exception as e:
            return JsonResponse({"Error": e.message})

        if CourseMode.can_auto_enroll(course_key):
            # Enroll the user using the default mode (audit)
            # We're assuming that users of the course enrollment table
            # will NOT try to look up the course enrollment model
            # by its slug.  If they do, it's possible (based on the state of the database)
            # for no such model to exist, even though we've set the enrollment type
            # to "audit".
            available_modes = CourseMode.modes_for_course_dict(course_key)
            try:
                enroll_mode = CourseMode.auto_enroll_mode(course_key, available_modes)
                if enroll_mode:
                    CourseEnrollment.enroll(student, course_key, check_access=True, mode=enroll_mode)
                    enroll_student = RequestEnroll.objects.get(student=student)
                    enroll_student.enrollment_status = 'granted'
                    enroll_student.save()
            except Exception as e:  # pylint: disable=broad-except
                return JsonResponse({'Error':e.message})

            return JsonResponse({'Student Enrolled':True})
    else:
        return JsonResponse({'Error':'User is not allowed to do this operation'})
    

def rejected(request,course_id,student_id):
    user = request.user
    if user.is_superuser:
        try:
            student = User.objects.get(id=student_id)
        except Exception as e:
            return JsonResponse({"Error":e.message})
        try:
            enroll_student = RequestEnroll.objects.get(student=student)
            enroll_student.enrollment_status = 'rejected'
            enroll_student.save()
        except Exception as e:
            return JsonResponse({'Error':e.message})

        return JsonResponse({'Student Rejected': True})
    else:
        return JsonResponse({'Error':'User is not allowed to do this operation'})