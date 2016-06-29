"""
WE'RE USING MIGRATIONS!

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the edx-platform dir
2. ./manage.py schemamigration course_progress --auto description_of_your_change
3. Add the migration file created in edx-platform/lms/djangoapps/course_progress/migrations/

"""
import json

from django.contrib.auth.models import User
from django.db import models

from model_utils.models import TimeStampedModel
from util.models import CompressedTextField
from xmodule_django.models import CourseKeyField, LocationKeyField

class StudentCourseProgress(TimeStampedModel):
    """
    Keeps course wise student course progress.
    """
    class Meta(object):
        app_label = "course_progress"
        unique_together = (('student', 'course_id'),)

    course_id = CourseKeyField(max_length=255, db_index=True, verbose_name='Course ID')

    student = models.ForeignKey(User, db_index=True)

    overall_progress = models.FloatField(default=0.0)

    progress_json = CompressedTextField(verbose_name='Progress JSON', blank=True, null=True)

    @property
    def progress(self):
        """
        Deserializes a course progress JSON object
        """
        if self.progress_json:
            return json.loads(self.progress_json)
        return None

    def __repr__(self):
        return 'StudenCourseProgress<%r>' % ({
            'course_id': self.course_id,
            'student_id': self.student_id,
            'overall_progress': str(self.overall_progress),
        },)

    def __unicode__(self):
        return unicode(repr(self))
