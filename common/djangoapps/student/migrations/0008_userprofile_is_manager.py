# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_userprofile_is_validator'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_manager',
            field=models.BooleanField(default=0),
        ),
    ]
