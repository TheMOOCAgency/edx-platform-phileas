# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0013_auto_20160816_0611'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoverview',
            name='manager_only',
            field=models.BooleanField(default=False),
        ),
    ]
