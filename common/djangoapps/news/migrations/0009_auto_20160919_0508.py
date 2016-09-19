# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_newspage_jacket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='title',
            field=models.CharField(default=b'Empty', max_length=255),
        ),
    ]
