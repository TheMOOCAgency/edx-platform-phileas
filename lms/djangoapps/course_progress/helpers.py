"""
Course progress helpers
"""
import json
from collections import OrderedDict

from django.conf import settings
from django.db import connection
from xmodule.modulestore.django import modulestore
from course_api.blocks.api import get_blocks

from student.models import CourseEnrollment
from course_progress.models import StudentCourseProgress


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

    if settings.FEATURES.get('TMA_COMPLETION_TRACKING'):
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

def item_affects_course_progress(request, suffix, handler, usage_id):
    suffix_list = [
        'problem_check',
        'hint_button',
        'lti_2_0_result_rest_handler',
    ]

    if suffix in suffix_list:
        return True
    elif suffix == 'save_user_state' and is_played(request):
        return True
    elif (handler == 'render_grade') and ('lti+block' in usage_id or 'lti_consumer+block' in usage_id or 'openassessment' in usage_id):
        return True

    return False

def is_played(request):
    time_str = request.POST.get('saved_video_position', '00:00:00')
    return sum(map(int, time_str.split(':'))) > 0

def get_default_course_progress(blocks, root):
    ordered_blocks = OrderedDict()
    if blocks:
        traverse_tree(root, blocks, ordered_blocks)
    return ordered_blocks

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

    for child_node in cur_block.get('children', []):
        traverse_tree(child_node, unordered_structure, ordered_blocks, parent=block)

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