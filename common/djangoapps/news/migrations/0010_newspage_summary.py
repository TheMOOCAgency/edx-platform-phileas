# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_auto_20160919_0508'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='summary',
            field=models.TextField(blank=True),
        ),
    ]
