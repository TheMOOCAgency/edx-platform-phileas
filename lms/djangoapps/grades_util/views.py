"""
Grades APIs
"""
import os
import csv
import glob
import urllib
import datetime


from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

import instructor_task.api

from courseware.courses import get_courses

from student.models import User 

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


@transaction.non_atomic_requests
def grade_report_generation(request):
    """
    For generating the reports of all the courses.
    """
    user = User.objects.get(pk=1)
    courses_list = []
    courses_list = get_courses(user)
    for course in courses_list:
        course_key =course.id
        try:
            instructor_task.api.submit_calculate_grades_csv(request, course_key)
            success_status = ("The grade report is being created."
                              " To view the status of the report, see Pending Tasks below.")

        except Exception as e:
            already_running_status = ("The grade report is currently being created."
                                       " To view the status of the report, see Pending Tasks below."
                                       " You will be able to download the report when it is complete.")
            print e.message
    merge_reports()
    return JsonResponse({"Reports Merged":"TRUE"})


def merge_reports():
    """
    Merges the reports of the courses
    """
    ignore_every_time = 0
    ignore_one_time = 0
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    for folder in os.listdir(settings.GRADES_DOWNLOAD['ROOT_PATH']):
        if os.path.isdir(folder):
            if folder.startswith("course"):
                folder_name = urllib.unquote_plus(folder).decode('utf8')
                course_name_array = folder_name.split(':')
                course_array = course_name_array[1].split('+')
                newest = max(glob.iglob('{}/*.csv'.format(folder)), key=os.path.getctime)

                with open(newest, 'rb') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',')

                    for row in spamreader:
                        if row[1] == "email" and ignore_every_time>=0:
                            if ignore_one_time == 0:
                                ignore_one_time = ignore_one_time+1

                                with open(settings.TMA_MERGED_REPORTS_PATH+settings.TMA_MERGED_REPORTS_NAME+date, 'a+') as csvfile:
                                    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                                    spamwriter.writerow(("course_org", "course_num", row[1], row[2], row[3]))

                            pass

                        else:
                            with open(settings.TMA_MERGED_REPORTS_PATH+settings.TMA_MERGED_REPORTS_NAME+date, 'a+') as csvfile:
                                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                                spamwriter.writerow((course_array[0], course_array[1], row[1], row[2], row[3]))
                    ignore_every_time = ignore_every_time + 1
