# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0014_courseoverview_manager_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='grade_badge',
            field=models.IntegerField(default=60),
        ),
    ]
