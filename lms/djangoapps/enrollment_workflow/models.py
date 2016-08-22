from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RequestEnroll(models.Model):
    STATUS_TYPES = (('requested', 'Requested'),
                    ('granted', 'Granted'),
                    ('rejected', 'Rejected'))
    course_id = models.CharField(max_length=200, db_index=True)
    student = models.ForeignKey(User, db_index=True)
    enrollment_status = models.CharField(max_length=32, choices=STATUS_TYPES, db_index=True)

    class Meta(object):
        unique_together = (('student', 'course_id'),)
