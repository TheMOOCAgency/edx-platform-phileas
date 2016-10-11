"""
Course progress helpers
"""
import json
from collections import OrderedDict

from django.db import connection
from xmodule.modulestore.django import modulestore
from course_api.blocks.api import get_blocks

from courseware.models import StudentModule
from openassessment.workflow.models import AssessmentWorkflow

from opaque_keys.edx.locations import BlockUsageLocator

from student.models import CourseEnrollment
from course_progress.models import StudentCourseProgress


# Valid components for tracking
VALID_COMPONENTS = ['video', 'problem', 'html', 'openassessment', 'lti']

VALID_BLOCKS = [
    'course', 'chapter', 'sequential', 'vertical'
] + VALID_COMPONENTS


def inject_course_progress_into_context(context, request, course_key):
    """
    Set params to view context based on course_key and user

    :param context: view context
    :type context: dict
    :param course_key: SlashSeparatedCourseKey instance
    :type course_key: SlashSeparatedCourseKey

    Author: Naresh Makwana
    """
    overall_progress = 0
    progress = {}

    try:
        student_course_progress = StudentCourseProgress.objects.get(student=request.user.id, course_id=course_key)
        overall_progress = student_course_progress.overall_progress
        progress = student_course_progress.progress
    except StudentCourseProgress.DoesNotExist:
        progress = set_initial_progress(request, course_key)

    context['overall_progress'] = overall_progress
    context['progress'] = progress

    context['is_rank_available'] = False
    student_rank, total_students = get_student_rank(request.user.id, course_key)
    if student_rank:
        context['is_rank_available'] = True
        context['student_rank'] = student_rank
        context['total_students'] = total_students

def get_student_rank(student_id, course_key):
    course_id = course_key.to_deprecated_string()
    total_students = CourseEnrollment.objects.filter(course_id=course_key, is_active=True).count()

    raw_query = """SELECT student_id FROM
        course_progress_studentcourseprogress WHERE
        course_id='"""+ course_id + """' AND
        overall_progress > 0
        ORDER BY overall_progress DESC;"""

    rows = []
    with connection.cursor() as cur:
        cur.execute(raw_query)
        rows = [int(row[0]) for row in cur.fetchall()]

    rank = None
    if student_id in rows:
        rank = rows.index(student_id) + 1

    return rank, total_students

def item_affects_course_progress(request, course_key, suffix, handler, instance):
    suffix_list = [
        'problem_check',
        'hint_button',
        'lti_2_0_result_rest_handler',
    ]

    if suffix in suffix_list:
        return True
    elif suffix == 'save_user_state' and is_played(request):
        return True
    else:
        usage_id = instance.location.to_deprecated_string()
        if suffix == 'grade_handler':
            if 'lti+block' in usage_id or 'lti_consumer+block' in usage_id:
                return True
        elif handler == 'render_grade':
            if 'openassessment' in usage_id:
                return is_assessed(request.user.id, course_key, instance)

    return False

def is_played(request):
    time_str = request.POST.get('saved_video_position', '00:00:00')
    return sum(map(int, time_str.split(':'))) > 0

def is_assessed(student_id, course_key, instance):
    state = get_component_state(student_id, course_key, instance)
    submission_uuid = state.get('submission_uuid')

    if submission_uuid:
        course_id = course_key.to_deprecated_string()
        item_id = instance.location.to_deprecated_string()
        try:
            workflow = AssessmentWorkflow.objects.get(course_id=course_id, item_id=item_id, submission_uuid=submission_uuid)
        except:
            return False

        return workflow.status == 'done'

    return False

def get_component_state(student_id, course_key, instance):
    try:
        history = StudentModule.objects.get(module_state_key=instance.location,
            student_id=student_id, course_id=course_key, module_type=instance.category)
    except:
        history = None

    return json.loads(history.state) if history and history.state else {}


def get_default_course_progress(blocks, root):
    default_course_progress = {}
    if blocks:
        default_course_progress = fix_block_ids(root, blocks)
    return default_course_progress

def traverse_tree(block, unordered_structure, ordered_blocks, parent=None):
    """
    Traverses the tree and fills in the ordered_blocks OrderedDict with the blocks in
    the order that they appear in the course.

    Also adds default progress for each block.
    """
    # find the dictionary entry for the current node
    cur_block = unordered_structure[block]
    cur_block.update({'progress': 0})

    if parent:
        cur_block['parent'] = parent

    ordered_blocks[block] = cur_block

    # Allow only tracking related elements
    for child_node in cur_block.get('children', []):
        if unordered_structure[child_node]['type'] in VALID_BLOCKS:
            traverse_tree(child_node, unordered_structure, ordered_blocks, parent=block)
        else:
            ordered_blocks[block]['children'].remove(child_node)

def set_initial_progress(request, course_key):
    course_usage_key = modulestore().make_course_usage_key(course_key)
    root = course_usage_key.to_deprecated_string()

    block_fields = ['type', 'display_name', 'children']
    course_struct = get_blocks(request, course_usage_key, request.user, 'all', requested_fields=block_fields)

    default_progress_dict = get_default_course_progress( course_struct.get('blocks', []), root )
    default_progress_json = json.dumps(default_progress_dict)
    student_course_progress = StudentCourseProgress.objects.create(
        student=request.user,
        course_id=course_key,
        progress_json=default_progress_json,
    )

    return student_course_progress.progress

def make_usage_id(course_key, category, url_name):
    return str(
        BlockUsageLocator(
            course_key, category, url_name
        )
    )

def get_overall_progress(student_id, course_key):
    """
    Get the course completion percent
    for the given student Id in given course.
    """
    overall_progress = 0

    try:
        student_course_progress = StudentCourseProgress.objects.get(student=student_id, course_id=course_key)
        overall_progress = student_course_progress.overall_progress
    except StudentCourseProgress.DoesNotExist:
        pass

    return overall_progress

def preserve_block_usage_id(block):
    # patch: block ID differs at API and LMS, if course imported
    original_block_id = block
    usage_key_splitted = block.split("+branch@draft")
    if len(usage_key_splitted) > 1:
        block_id_type_part = usage_key_splitted[1].split("+type@")[1]
        original_block_id = usage_key_splitted[0] + "+type@" + block_id_type_part

    return original_block_id

def fix_block_ids(course_key, blocks):
    modified_course_struct = {}
    modified_course_block = {}
    modified_course_block_children = []

    course_block = blocks[course_key]
    for chapter_id in course_block.get('children', []):
        modified_chapter_id = preserve_block_usage_id(chapter_id)
        modified_chapter_block = {}
        modified_chapter_block_children = []

        chapter_block = blocks[chapter_id]
        for sequential_id in chapter_block.get('children', []):
            modified_sequential_id = preserve_block_usage_id(sequential_id)
            modified_chapter_block = {}
            modified_sequential_block_children = []

            sequential_block = blocks[sequential_id]
            for vertical_id in sequential_block.get('children', []):
                modified_vertical_id = preserve_block_usage_id(vertical_id)
                modified_vertical_block = {}
                modified_vertical_block_children = []

                vertical_block = blocks[vertical_id]
                for component_id in vertical_block.get('children', []):
                    if blocks[component_id]['type'] in VALID_COMPONENTS:
                        modified_component_id = preserve_block_usage_id(component_id)
                        component_block = blocks[component_id]
                        component_block['id'] = modified_component_id
                        component_block['parent'] = modified_vertical_id
                        component_block['progress'] = 0
                        modified_course_struct.update({
                            modified_component_id: component_block
                        })
                        modified_vertical_block_children += [modified_component_id]

                vertical_block['id'] = modified_vertical_id
                vertical_block['parent'] = modified_sequential_id
                vertical_block['children'] = modified_vertical_block_children
                vertical_block['progress'] = 0
                modified_course_struct.update({
                    modified_vertical_id: vertical_block
                })
                modified_sequential_block_children += [modified_vertical_id]

            sequential_block['id'] = modified_sequential_id
            sequential_block['parent'] = modified_chapter_id
            sequential_block['children'] = modified_sequential_block_children
            sequential_block['progress'] = 0
            modified_course_struct.update({
                modified_sequential_id: sequential_block
            })
            modified_chapter_block_children += [modified_sequential_id]

        chapter_block['id'] = modified_chapter_id
        chapter_block['parent'] = course_key
        chapter_block['children'] = modified_chapter_block_children
        chapter_block['progress'] = 0
        modified_course_struct.update({
            modified_chapter_id: chapter_block
        })
        modified_course_block_children += [modified_chapter_id]
    course_block['children'] = modified_course_block_children
    course_block['progress'] = 0
    modified_course_struct.update({
        course_key: course_block
    })

    return modified_course_struct