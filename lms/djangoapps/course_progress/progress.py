import json
from collections import OrderedDict

from openassessment.workflow.models import AssessmentWorkflow
from xmodule.modulestore.django import modulestore
from course_api.blocks.api import get_blocks

from course_progress.models import StudentCourseProgress
from course_progress.helpers import get_default_course_progress


def update_course_progress(request, course_key, module_type, usage_keys):
    """
    Description: To calculate and update the course progress
    for specified student and course.

    Arguments:
        request: HTTPRequest obj
        course_key: SlashSeparatedCourseKey instance, identifying the course
        instance: progress affecting xblock module
        module_type: type of the xblock i.e. problem, video etc.
        usage_keys: list of usage key instances

    Notes:
        For each Block traversed, the following is verified and
        the block is excluded when not accessible by the user.
            1. Block is not visible_to_staff_only
            2. The Block has been released
            3. The cohort affiliation of the Block matches the requested user's cohort

    Author: Naresh Makwana
    """
    # Initialization
    student = request.user
    course_struct = {}
    root = None
    course_progress = {}
    chapter_wise_progress = OrderedDict()

    # Get course structure
    course_usage_key = modulestore().make_course_usage_key(course_key)
    root = course_usage_key.to_deprecated_string()

    block_fields = ['type', 'display_name', 'children']
    course_struct = get_blocks(request, course_usage_key, request.user, 'all', requested_fields=block_fields)

    # get course progress object
    try:
        student_course_progress = StudentCourseProgress.objects.get(student=student.id, course_id=course_key)
    except StudentCourseProgress.DoesNotExist:
        default_progress_dict = get_default_course_progress( course_struct.get('blocks', []), root )
        default_progress_json = json.dumps(default_progress_dict)
        student_course_progress = StudentCourseProgress.objects.create(
            student=student,
            course_id=course_key,
            progress_json=default_progress_json,
        )


    # Get course progress dict
    progress = student_course_progress.progress

    # To have proper sync with blocks and stored progress
    new_progress = {}
    default_progress_dict = get_default_course_progress( course_struct.get('blocks', []), root )
    for default_block_id, default_block in default_progress_dict.items():
        progress_block = progress.get(default_block_id, {})
        stored_progress = progress_block.get('progress', 0)
        default_block.update({'progress': stored_progress})
        new_progress.update({default_block_id: default_block})
    progress = new_progress

    # increase progress if attempted or graded and not already updated
    updated_units = []
    for usage_key in usage_keys:
        usage_id = usage_key.to_deprecated_string()
        current_progress = progress.get(usage_id, {}).get('progress')
        if current_progress != 100:
            progress[usage_id]['progress'] = 100
            updated_units.append(progress[usage_id]['parent'])

    # update unit progress
    if updated_units:
        update_unit_progress(progress, list(set(updated_units)) )

    student_course_progress.progress_json = json.dumps(progress)
    student_course_progress.overall_progress = progress[root]['progress']
    student_course_progress.save()

def update_unit_progress(progress, unit_ids):
    updated_sequentials = []
    for unit_id in unit_ids:
        total_components_completed = 0
        total_components = len(progress[unit_id]['children'])
        for component_id in progress[unit_id]['children']:
            if progress[component_id]['progress'] == 100:
                total_components_completed += 1
        unit_progress = round(total_components_completed * 100 / total_components)
        progress[unit_id]['progress'] = unit_progress
        updated_sequentials.append(progress[unit_id]['parent'])

    # update sequential progress
    if updated_sequentials:
        update_sequential_progress(progress, list(set(updated_sequentials)) )

def update_sequential_progress(progress, sequential_ids):
    updated_chapters = []
    for sequential_id in sequential_ids:
        total_units_completed = 0
        total_units = len(progress[sequential_id]['children'])
        for unit_id in progress[sequential_id]['children']:
            if progress[unit_id]['progress'] == 100:
                total_units_completed += 1
        sequential_progress = round(total_units_completed * 100 / total_units)
        progress[sequential_id]['progress'] = sequential_progress
        updated_chapters.append(progress[sequential_id]['parent'])

    # update chapter progress
    if updated_chapters:
        update_chapter_progress(progress, list(set(updated_chapters)) )

def update_chapter_progress(progress, chapter_ids):
    updated_course = None
    for chapter_id in chapter_ids:
        sum_sequentials_progress = 0
        total_sequentials = len(progress[chapter_id]['children'])
        for sequential_id in progress[chapter_id]['children']:
            sum_sequentials_progress += progress[sequential_id]['progress']
        chapter_progress = round(sum_sequentials_progress / total_sequentials)
        progress[chapter_id]['progress'] = chapter_progress
        updated_course = progress[chapter_id]['parent']

    # update course progress
    if updated_course:
        update_root_progress(progress, updated_course)

def update_root_progress(progress, course_id):
    sum_chapter_progress = 0
    total_chapters = len(progress[course_id]['children'])
    for chapter_id in progress[course_id]['children']:
        sum_chapter_progress += progress[chapter_id]['progress']
    course_progress = round(sum_chapter_progress / total_chapters)
    progress[course_id]['progress'] = course_progress