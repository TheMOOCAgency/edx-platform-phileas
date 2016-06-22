"""
WE'RE USING MIGRATIONS!

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the edx-platform dir
2. ./manage.py schemamigration course_progress --auto description_of_your_change
3. Add the migration file created in edx-platform/lms/djangoapps/course_progress/migrations/

"""
from django.contrib.auth.models import User
from django.db import models

from xmodule_django.models import CourseKeyField, LocationKeyField


class StudentHistory(models.Model):
    """
    Keeps student state for a particular module in a particular course.
    """
    MODEL_TAGS = ['course_id', 'module_type']

    # For a homework problem, contains a JSON
    # object consisting of state
    MODULE_TYPES = (('problem', 'problem'),
                    ('video', 'video'),
                    ('html', 'html'),
                    ('course', 'course'),
                    ('chapter', 'Section'),
                    ('sequential', 'Subsection'),
                    ('library_content', 'Library Content'))
    ## These three are the key for the object
    module_type = models.CharField(max_length=32, choices=MODULE_TYPES, default='problem', db_index=True)

    # Key used to share state. This is the XBlock usage_id
    module_state_key = LocationKeyField(max_length=255, db_index=True, db_column='module_id')
    student = models.ForeignKey(User, db_index=True)

    course_id = CourseKeyField(max_length=255, db_index=True)

    class Meta(object):
        app_label = "course_progress"
        unique_together = (('student', 'module_state_key', 'course_id'),)

    DONE_TYPES = (
        ('f', 'FINISHED'),
        ('i', 'INCOMPLETE'),
    )
    done = models.CharField(max_length=8, choices=DONE_TYPES, default='na', db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return 'StudentHistory<%r>' % ({
            'course_id': self.course_id,
            'module_type': self.module_type,
            'student_id': self.student_id,
            'module_state_key': self.module_state_key,
            'done': str(self.done),
        },)

    def __unicode__(self):
        return unicode(repr(self))
