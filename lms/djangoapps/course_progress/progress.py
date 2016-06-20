import json
from collections import OrderedDict

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from courseware.courses import get_course_by_id
from courseware.models import StudentModule


@login_required
@ensure_csrf_cookie
def get_course_progress(request):
    """
    Description: This view kept for calculationg the course progress
    for the given student in a particular course.

    Arguments:
        course_id: course ID for which progress needs to be calculated.
        student_id: Student for which progress needs to be calculated.

    Author: Naresh Makwana
    """
    progress = {}
    include_items = ['video', 'problem', 'html']
    sections = OrderedDict()

    course_id = request.GET.get('course_id')
    student_id = request.user.id

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_by_id(course_key)

    student_module_history = StudentModule.objects.filter(student_id=student_id, course_id=course_key)

    for section in course.get_children():
        if not section.visible_to_staff_only and section.start < timezone.now():
            sub_sections = OrderedDict()
            for sub_section in section.get_children():
                if not sub_section.visible_to_staff_only and sub_section.start < timezone.now():
                    units = OrderedDict()
                    unit_attempted = 0
                    for unit in sub_section.get_children():
                        if not unit.visible_to_staff_only and unit.start < timezone.now():
                            component_count = 0
                            component_attempted = 0
                            for component in unit.get_children():
                                if not unit.visible_to_staff_only and component.start < timezone.now():
                                    if component.category in include_items:
                                            component_count += 1

                                            try:
                                                history = StudentModule.objects.get(module_state_key=component.location, module_type=component.category)
                                            except:
                                                history = None

                                            if history:
                                                if component.category == 'problem' and json.loads(history.state).get('attempts', 0):
                                                    component_attempted +=1
                                                elif component.category == 'video' and is_played(json.loads(history.state).get('saved_video_position', '00:00:00')):
                                                    component_attempted +=1

                            unit_progress = round(component_attempted * 100.00 / component_count, 2)
                            if unit_progress == 100:
                                unit_attempted += 1
                            units.update({str(unit.display_name_with_default): unit_progress})
                    sub_section_progress = round(unit_attempted * 100.00 / len(units.keys()), 2)
                    sub_sections.update({
                        str(sub_section.display_name_with_default): {
                            'sub_section_progress': sub_section_progress,
                            'units': units
                        }
                    })
            sub_section_progress_sum = sum([sub_section_dict.get('sub_section_progress', 0.0) for sub_section_dict in sub_sections.values()])
            section_progress = round(sub_section_progress_sum * 1.00 / len(sub_sections.keys()), 2)
            sections.update({
                str(section.display_name_with_default): {
                    'section_progress': section_progress,
                    'sub_sections': sub_sections
                }
            })

    section_progress_sum = sum([section_dict.get('section_progress', 0.0) for section_dict in sections.values()])
    course_progress = round(section_progress_sum * 1.00 / len(sections.keys()), 2)
    progress.update({
        'course_progress': course_progress,
        'sections': sections
    })

    return JsonResponse(progress)

def is_played(time_str):
    return sum(map(int, time_str.split(':'))) > 0
