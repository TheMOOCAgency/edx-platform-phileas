import json
from collections import OrderedDict

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from openassessment.workflow.models import AssessmentWorkflow

from courseware.courses import get_course_by_id
from courseware.models import StudentModule
from course_progress.models import StudentHistory


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
    include_items = ['video', 'problem', 'html', 'openassessment']
    sections = OrderedDict()

    course_id = request.GET.get('course_id')
    student_id = request.user.id

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_by_id(course_key)

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
                                            component_attempted += is_attempted(student_id, course_key, component)
                            unit_progress = 0.0
                            if component_count:
                                unit_progress = round(component_attempted * 100.00 / component_count, 2)
                            if unit_progress == 100:
                                unit_attempted += 1
                            units.update({str(unit.display_name_with_default): unit_progress})
                    sub_section_progress = 0.0
                    if units:
                        sub_section_progress = round(unit_attempted * 100.00 / len(units.keys()), 2)
                    sub_sections.update({
                        str(sub_section.display_name_with_default): {
                            'sub_section_progress': sub_section_progress,
                            'units': units
                        }
                    })
            sub_section_progress_sum = sum([sub_section_dict.get('sub_section_progress', 0.0) for sub_section_dict in sub_sections.values()])
            section_progress = 0.0
            if sub_sections:
                section_progress = round(sub_section_progress_sum * 1.00 / len(sub_sections.keys()), 2)
            sections.update({
                str(section.display_name_with_default): {
                    'section_progress': section_progress,
                    'sub_sections': sub_sections
                }
            })

    section_progress_sum = sum([section_dict.get('section_progress', 0.0) for section_dict in sections.values()])
    course_progress = 0.0
    if sections:
        course_progress = round(section_progress_sum * 1.00 / len(sections.keys()), 2)
    progress.update({
        'course_progress': course_progress,
        'sections': sections
    })

    return JsonResponse(progress)

def is_played(time_str):
    return sum(map(int, time_str.split(':'))) > 0

def is_attempted(student_id, course_key, component):
    attempted = 0
    state = get_component_state(component.location, student_id, course_key, component.category)

    if component.category == 'problem':
        if state.has_key('attempts'):
            attempted = 1
        elif get_component_done(component.location, student_id, course_key, component.category):
            attempted = 1
    elif component.category == 'video' and is_played(state.get('saved_video_position', '00:00:00')):
        attempted = 1
    elif component.category == 'html' and get_component_done(component.location, student_id, course_key, component.category):
        attempted = 1
    elif component.category == 'openassessment':
        submission_uuid = state.get('submission_uuid')
        course_id = course_key.to_deprecated_string()
        item_id = component.location.to_deprecated_string()
        if submission_uuid and is_assessed(course_id, item_id, submission_uuid):
            attempted = 1

    return attempted

def get_component_state(module_state_key, student_id, course_key, module_type):
    try:
        history = StudentModule.objects.get(module_state_key=module_state_key,
            student_id=student_id, course_id=course_key, module_type=module_type)
    except:
        history = None
    
    return json.loads(history.state) if history and history.state else {}

def is_assessed(course_id, item_id, submission_uuid):
    try:
        workflow = AssessmentWorkflow.objects.get(course_id=course_id, item_id=item_id, submission_uuid=submission_uuid)
    except:
        return False

    return workflow.status == 'done'

def get_component_done(module_state_key, student_id, course_key, module_type):
    try:
        history = StudentHistory.objects.get(module_state_key=module_state_key,
            student_id=student_id, course_id=course_key, module_type=module_type)
    except:
        history = None

    return history and history.done == 'f'
