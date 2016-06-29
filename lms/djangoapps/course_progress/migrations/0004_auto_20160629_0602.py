# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('course_progress', '0003_auto_20160627_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentcourseprogress',
            name='course_id',
            field=xmodule_django.models.CourseKeyField(max_length=255, verbose_name=b'Course ID', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='studentcourseprogress',
            unique_together=set([('student', 'course_id')]),
        ),
    ]
