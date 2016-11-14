# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0012_auto_20160816_0536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseoverview',
            name='enrollment_workflow',
            field=models.TextField(null=True),
        ),
    ]
