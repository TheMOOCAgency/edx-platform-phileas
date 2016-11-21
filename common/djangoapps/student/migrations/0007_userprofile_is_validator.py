# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_logoutviewconfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_validator',
            field=models.BooleanField(default=0),
        ),
    ]
