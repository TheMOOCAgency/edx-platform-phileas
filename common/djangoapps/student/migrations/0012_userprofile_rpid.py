# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_auto_20161007_0457'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rpid',
            field=models.CharField(db_index=True, max_length=50, null=True, blank=True),
        ),
    ]
