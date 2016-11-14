# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment_workflow', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='requestenroll',
            unique_together=set([('student', 'course_id')]),
        ),
    ]
