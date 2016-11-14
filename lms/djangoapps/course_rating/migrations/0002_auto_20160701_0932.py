# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_rating', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courserating',
            old_name='student_id',
            new_name='student',
        ),
        migrations.AlterUniqueTogether(
            name='courserating',
            unique_together=set([('student', 'course_id')]),
        ),
    ]
