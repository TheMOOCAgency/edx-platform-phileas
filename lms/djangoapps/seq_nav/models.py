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

from model_utils.models import TimeStampedModel

class StudentUnitVisit(TimeStampedModel):
    """
    Keeps course wise student course progress.
    """
    class Meta(object):
        app_label = "seq_nav"
        unique_together = (('student', 'unit_id'),)

    student = models.ForeignKey(User, db_index=True)

    unit_id = models.CharField(max_length=255)

    visited = models.BooleanField(default=False)

    def __repr__(self):
        return 'StudentUnitVisit<%r>' % ({
            'student_id': self.student_id,
            'unit_id': str(self.unit_id),
            'visited': str(self.visited),
        },)

    def __unicode__(self):
        return unicode(repr(self))
