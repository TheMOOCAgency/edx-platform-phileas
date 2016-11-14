# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_progress', '0002_studentcourseprogress'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studenthistory',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='studenthistory',
            name='student',
        ),
        migrations.DeleteModel(
            name='StudentHistory',
        ),
    ]
