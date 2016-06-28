"""
Course progress helpers
"""
from collections import OrderedDict

from django.conf import settings

from course_progress.models import StudentCourseProgress

def inject_course_progress_into_context(context, user, course_key):
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
    student_rank = 'NA'

    if settings.FEATURES.get('TMA_COMPLETION_TRACKING'):
        try:
            student_course_progress = StudentCourseProgress.objects.get(student=user.id, course_id=course_key)
            overall_progress = student_course_progress.overall_progress
            progress = student_course_progress.progress
        except StudentCourseProgress.DoesNotExist:
            pass

    context['overall_progress'] = overall_progress
    context['progress'] = progress

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

def get_default_course_progress(course_obj):
    ordered_blocks = OrderedDict()
    if course_obj.structure:
        traverse_tree(course_obj.structure['root'], course_obj.structure['blocks'], ordered_blocks)
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

    for child_node in cur_block['children']:
        traverse_tree(child_node, unordered_structure, ordered_blocks, parent=block)