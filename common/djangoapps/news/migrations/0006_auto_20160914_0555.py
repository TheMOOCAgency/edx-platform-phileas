# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20160912_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
