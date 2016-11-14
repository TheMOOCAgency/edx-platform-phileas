# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0011_courseoverview_enrollment_workflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseoverview',
            name='enrollment_workflow',
            field=models.TextField(default=b'nre'),
        ),
    ]
