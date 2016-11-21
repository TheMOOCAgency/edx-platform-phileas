
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_userprofile_rpid'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='badge_grade',
            field=models.IntegerField(default=60),
        ),
    ]
